from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    frequently_bought_ids = fields.Many2many(
        'product.product',
        'product_frequently_bought_rel',
        'product_id',
        'frequently_bought_id',
        string='Frequently Bought Together',
        help='IDs of products frequently bought together'
    )
