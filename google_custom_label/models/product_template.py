from odoo import models, fields, api

class GoogleCustomLabel(models.Model):
    _name = 'google.custom.label'
    _description = 'Google Custom Label'

    name = fields.Char(string='Name', required=True)
    _sql_constraints = [('google_custom_label_uniq',
                         'UNIQUE (name)',
                         'Google custom label Name must be unique.')]

    @api.model
    def create(self, vals):
        custom_label = super(GoogleCustomLabel, self).create(vals)
        product_templates = self.env['product.template'].search([('google_custom_label', '=', False)])
        for product in product_templates:
            product.write({'google_custom_label': custom_label.id})
        return custom_label


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    google_custom_label = fields.Many2one(comodel_name='google.custom.label', string='Google Custom Label')

    @api.onchange('google_custom_label')
    def _onchange_google_custom_label(self):
        for variant in self.product_variant_ids:
            variant.google_custom_label = self.google_custom_label

class ProductProduct(models.Model):
    _inherit = 'product.product'

    google_custom_label = fields.Many2one(comodel_name='google.custom.label', string='Google Custom Label', related='product_tmpl_id.google_custom_label', store=True)
