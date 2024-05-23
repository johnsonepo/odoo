import pycountry
import json
import requests
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):
    AFTER_TABBY_PAYMNT = []
    @http.route(['/get_tabby_data'], type='json', auth="public", website=True)
    def get_tabby_data(self, **kw):
        res = {}
        tabby_id = request.env['payment.provider'].sudo().search([('code', '=', 'tabby')], limit=1)
        tx = request.env['payment.transaction'].sudo().search([], limit=1)
        if tx:
            res['cust_email'] = tx.partner_id.email
            res['cust_phone'] = tx.partner_id.phone
            res['cust_street'] = tx.partner_id.street
            res['cust_city'] = tx.partner_id.city
            res['cust_zip'] = tx.partner_id.zip
            res['cust_state_code'] = tx.partner_id.state_id.name
            if len(tx.partner_id.country_id.code) == 2:
                try:
                    country = pycountry.countries.get(alpha_2=(tx.partner_id.country_id.code).upper())
                    res['cust_country'] = country.alpha_3
                except Exception as e:
                    raise ValueError("Exception-", e)
            else:
                res['cust_country'] = (tx.partner_id.country_id.code).upper()

            res['amount'] = tx.amount
            res['currency'] = tx.currency_id.name

        for sale_order in tx.sale_order_ids:
            for line in sale_order.order_line:
                res['product_name'] = line.product_id.name
                res['order_name'] = tx.reference
                res['order_id'] = tx.id

        if tabby_id:
            res['merchant_id'] = tabby_id.tabby_merchant_id
            res['merchant_key'] = tabby_id.tabby_public_key
            res['address1'] = tabby_id.address1
            res['address2'] = tabby_id.address2
            res['interaction.operation'] = 'PURCHASE'

        # Prepare data for Tabby API request
        tabby_data = {
            'amount': res['amount'],
            'currency': res['currency'],
            'description': tx.reference,
            'buyer': {
                'phone': res['cust_phone'],
                'email': res['cust_email'],
                'name': res['cust_email'],
            },
            'order': {
            },
            'meta': {
                'order_id': res['order_id'],
                'customer': res['cust_email'],
            },
        }
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        cancel_url = base_url + '/shop/payment'
        return_url = base_url + '/shop/completeCallback'
        try:
            url = 'https://api.tabby.ai/api/v2/checkout'

            payload = {
                "payment": {
                    "amount": res['amount'],
                    "currency": res['currency'],
                    "description": tx.reference,
                    "buyer": {
                        'phone': res['cust_phone'],
                        'email': res['cust_email'],
                        'name': res['cust_email'],
                    },
                    "shipping_address": {
                        "city":  res['cust_city'],
                        "address": res['cust_street'],
                        "zip": res['cust_zip'],
                    },
                    "order": {},
                    "buyer_history": {},
                    "order_history": [],
                    "meta": {
                        'order_id': res['order_id'],
                        'customer': res['cust_email'],
                    },
                },
                "lang": "ar",
                "merchant_code":  res['merchant_id'],
                "merchant_urls": {
                    "success": return_url,
                    "cancel": cancel_url,
                    "failure": "/"
                },
                "create_token": False,
                "token": None
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + res['merchant_key'],
            }

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                session_data = response.json()

                session_id = session_data['id']
                web_url = session_data['configuration']['available_products']['installments'][0]['web_url']
                res['re_url'] = web_url

                self.AFTER_TABBY_PAYMNT = session_data
                return res

            else:
                print("Error:", response.text)

        except Exception as e:
            # Exception occurred while sending request or parsing response
            error_message = f"Error occurred: {str(e)}"
            return {'error': error_message}

    @http.route(['/shop/completeCallback'], type='http', auth="public", website=True)
    def confirm_order_new(self, **post):
        tabby_data = {}
        tabby_data['session_id'] = self.AFTER_TABBY_PAYMNT.get('payment', {}).get('id')
        tabby_data['order_id'] = self.AFTER_TABBY_PAYMNT.get('payment', {}).get('description')
        installments_data = self.AFTER_TABBY_PAYMNT.get('configuration', {}).get('available_products', {}).get('installments', [])

        if installments_data:
            for installment in installments_data:
                tabby_data['installment_id'] = installment.get('id')
                tabby_data['down_payment'] = installment.get('downpayment')
                tabby_data['amount_to_pay'] = installment.get('amount_to_pay')
                tabby_data['web_url'] = installment.get('web_url')
                tabby_data['order_amount'] = installment.get('order_amount')
                tabby_data['qr_code'] = installment.get('qr_code')
        else:
            print("Installments data not found in the data.")

        payment_transaction = request.env['payment.transaction'].sudo().search([], limit=1)
        payment_transaction._process_notification_data(post, tabby_data)
        return request.redirect('/shop/confirmation')