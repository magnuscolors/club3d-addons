# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = "res.company"

    freight_cost_account = fields.Many2one(
        'account.account', 'Freight Cost Account',
        domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
        help="Freight cost/debit Account.")

    freight_reservation_account = fields.Many2one(
        'account.account', 'Freight Reservation Account',
        domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
        help="Freight cost/credit Account.")

    freight_product = fields.Many2one('product.product',
          string='Freight Product',
          help="Freight product for journal entries.")


