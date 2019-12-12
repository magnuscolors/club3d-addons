# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    upc_code = fields.Char('UPC Code', size=12)
    net_weight = fields.Float(
        'Net Weight', compute='_compute_net_weight', digits=dp.get_precision('Stock Weight'),
        inverse='_set_net_weight', store=True, help="The net weight of the contents in Kg, not including any packaging, etc.")

    @api.depends('product_variant_ids', 'product_variant_ids.net_weight')
    def _compute_net_weight(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.net_weight = template.product_variant_ids.net_weight
        for template in (self - unique_variants):
            template.net_weight = 0.0

    @api.one
    def _set_net_weight(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.net_weight = self.net_weight

class ProductProduct(models.Model):
    _inherit = "product.product"

    net_weight = fields.Float(
        'Net Weight', digits=dp.get_precision('Stock Weight'),
        help="The net weight of the contents in Kg, not including any packaging, etc.")


#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100