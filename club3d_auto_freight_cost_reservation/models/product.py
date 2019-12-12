# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductCategory(models.Model):
    _inherit = 'product.category'

    automate_freight_cal = fields.Boolean('Automate Freight Calculation')
    debit_freight_percentage = fields.Float("Debit Freight %", default=1)

    @api.constrains('automate_freight_cal', 'debit_freight_percentage')
    def _check_debit_freight_percentage(self):
        if self.automate_freight_cal and not self.debit_freight_percentage:
            raise ValidationError(_("Error! Must set debit Freight %"))