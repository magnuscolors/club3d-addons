# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.purchase_line_id:
            res.partner_id = res.purchase_line_id.partner_id.id
        return res