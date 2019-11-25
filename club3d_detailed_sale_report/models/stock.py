# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.depends('quantity_done')
    def _qty_done_compute(self):
        for move in self:
            move.done_qty = move.quantity_done
            if move.location_dest_id.usage == 'customer':
                move.done_qty = -move.done_qty


    done_qty = fields.Float('Quantity Done456', compute='_qty_done_compute', digits=dp.get_precision('Product Unit of Measure'), store=True)

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.purchase_line_id:
            res.partner_id = res.purchase_line_id.partner_id.id
        return res