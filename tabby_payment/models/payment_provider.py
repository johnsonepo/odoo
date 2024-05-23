import logging
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.http import request
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['tabby'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res


class ProviderTabby(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('tabby', 'Tabby')], ondelete={'tabby': 'set default'})
    tabby_merchant_id = fields.Char(string='Tabby Merchant Code', required_if_provider='tabby', groups='base.group_user')
    tabby_public_key = fields.Char(string='Tabby Public Key', required_if_provider='tabby', groups='base.group_user')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tabby_data = fields.Text(string='Tabby Data')


class PaymentTxTabby(models.Model):
    _inherit = 'payment.transaction'

    def _process_notification_data(self, notification_data, tabby_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != "tabby":
            return

        sale_order = self.env['sale.order'].search([('name', '=', tabby_data.get('order_id'))])
        if sale_order:
            sale_order_id = sale_order.id
            sale_order = self.env['sale.order'].browse(sale_order_id)
            sale_order.write({'tabby_data': tabby_data})
            self.env.cr.commit()

        self._set_done()
        self.with_context({'tabby': True})._reconcile_after_done()

    def _reconcile_after_done(self):
        """ Override of payment to automatically confirm quotations and generate invoices. """
        if self._context.get('tabby'):
            sales_orders = self.mapped('sale_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
            for tx in self:
                pass

            # send order confirmation mail
            sales_orders._send_order_confirmation_mail()
            # invoice the sale orders if needed
            self._invoice_sale_orders()
            if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice') and any(
                    so.state in ('sale', 'done') for so in self.sale_order_ids):
                default_template = self.env['ir.config_parameter'].sudo().get_param(
                    'sale.default_invoice_email_template')
                if default_template:
                    for trans in self.filtered(
                            lambda t: t.sale_order_ids.filtered(lambda so: so.state in ('sale', 'done'))):
                        trans = trans.with_company(trans.provider_id.company_id).with_context(
                            mark_invoice_as_sent=True,
                            company_id=trans.provider_id.company_id,
                        )
                        for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
                            invoice.message_post_with_template(int(default_template),
                                                               email_layout_xmlid="mail.mail_notification_light")
                self.invoice_ids.filtered(lambda inv: inv.state == 'draft').action_post()

                # Create and post missing payments for transactions requiring reconciliation
                for tx in self.filtered(lambda t: t.operation != 'validation' and not t.payment_id):
                    tx._create_payment()
        else:
            return super()._reconcile_after_done()

