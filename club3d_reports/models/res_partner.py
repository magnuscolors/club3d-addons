# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipping_company_name = fields.Char(string='Shipping Company Name', copy=False)
