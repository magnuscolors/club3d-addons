# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def get_delivery_details(self):
        res = {}
        self.ensure_one()
        if self.move_ids:
            picking_ids = self.move_ids.picking_ids.search(
                [('state', 'in', ('confirmed', 'ready'))])
            picking_date = picking_ids.filtered(lambda p: not p.backorder_id) or False
            picking_bck_orders = picking_ids.filtered(lambda p: p.backorder_id) or False
        if picking_date:
            res.update({'date': datetime.strptime(picking_date.scheduled_date, '%Y-%m-%d %H:%M:%S').date(), 'back_ref':False})
            if picking_bck_orders:
                bck_ord_ref = ','.join([o.name for o in picking_bck_orders])
                res.update({'back_ref':bck_ord_ref})
        return res