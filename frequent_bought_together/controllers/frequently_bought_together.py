import json
from odoo import http
from odoo.http import request
from collections import Counter

class FrequentlyBoughtTogether(http.Controller):
    """ Getting product details and passing returning
        the values and rendering the templates from js"""

    @http.route('/get/frequently_bought_together', type='json', auth='public', website=True)
    def search_sales_report(self, **kw):
        SaleOrderLine = request.env['sale.order.line']
        request_body = json.loads(request.httprequest.data)
        product_id_str = request_body['product_id']
        product_id = 0

        if not product_id_str:
            return {'error': 'Product ID not provided'}

        try:
            product_id = int(product_id_str)
        except ValueError:
            return {'error': 'Invalid Product ID'}

        #print(f'Product ID: {product_id}')

        sale_order_lines = SaleOrderLine.search([('product_id', '=', product_id)])
                
        print(sale_order_lines)


        sale_order_ids = sale_order_lines.mapped('order_id').ids
        sale_orders_data = sale_order_ids

        sale_order_lines = request.env['sale.order.line'].search([('order_id', 'in', sale_order_ids)])

        product_ids = [line.product_id.id for line in sale_order_lines] 
        product_ids = [id for id in product_ids if id != product_id]

        product_id_counts = Counter(product_ids)

        summed_product_counts = {}
        for product_id, count in product_id_counts.items():
            if product_id in summed_product_counts:
                summed_product_counts[product_id] += count
            else:
                summed_product_counts[product_id] = count

        sorted_product_counts = sorted(summed_product_counts.items(), key=lambda x: x[1], reverse=True)

        top_product_ids = {}

        for product_id, count in sorted_product_counts[:15]:
            top_product_ids[product_id] = count

        top_product_info = {}

        exclude_terms = ['delivery', 'shipping', 'carrier', 'courier', 'undefined']

        for pro_id in top_product_ids:
            product = request.env['product.product'].sudo().browse(int(pro_id))
            count = 0
            if product.exists() and product and not any(term.lower() in product.name.lower() for term in exclude_terms) and product.qty_available > 0:
                product_info = {
                    'id': product.id,
                    'name': product.name,
                    'on_hand_quantity': product.qty_available,
                    'price': product.list_price,
                    'internal_ref': product.default_code,
                    'url': product.website_url,
                    'image_link': '/web/image/product.product/{}/image_1024'.format(product.id),
                }
                top_product_info[pro_id] = product_info
            else:
                top_product_info[pro_id] = {'error': 'Product not found or excluded'}

        top_product_info = dict(list(top_product_info.items())[:7])
        #top_product_info_json = top_product_info #json.dumps(list(top_product_info.values()), indent=2)
        #print('Top 6 Product Info:', top_product_info_json)

        pos_order_lines = request.env['pos.order.line'].search([('product_id', '=', product_id)])
        pos_order_ids = pos_order_lines.mapped('order_id.id')
        pos_orders = request.env['pos.order'].browse(pos_order_ids)

        pos_orders_data = [{
            'id': order.id,
            'name': order.name,
            'date_order': order.date_order,
            'amount_total': order.amount_total,
        } for order in pos_orders]

        return {
            'sale_orders': top_product_info,
            'pos_orders': pos_orders_data,
        }