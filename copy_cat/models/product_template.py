from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_facebook_ads = fields.Boolean(string='Allow Facebook Ads', default=True)
    allow_google_ads = fields.Boolean(string='Allow Google Ads', default=True)
    allow_snapchat_ads = fields.Boolean(string='Allow Snapchat Ads', default=False)

