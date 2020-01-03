# -*- coding: utf-8 -*-

from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo import models, fields, api, _
from datetime import datetime

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False,
            submenu=False):

        result = super(SaleOrderLine, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        group_club3d_restricted = self.user_has_groups('club3d_account.group_club3d_restricted')
        if view_type == 'form' and not group_club3d_restricted:
            doc = etree.XML(result['arch'])
            node = doc.xpath("//field[@name='purchase_price']")[0]
            node.set('invisible', '1')
            setup_modifiers(node, result['fields']['purchase_price'])

            node = doc.xpath("//field[@name='margin']")[0]
            node.set('invisible', '1')
            setup_modifiers(node, result['fields']['margin'])

            result['arch'] = etree.tostring(doc, encoding='unicode')

        return result

    @api.multi
    def get_delivery_details(self):
        res = {'delivery_date': False, 'expected_date': False, 'done_back_ref': False, 'back_ref': False}
        self.ensure_one()
        if self.move_ids:
            picking_ids = self.move_ids.mapped('picking_id')
            qty_dict = dict(zip(picking_ids.ids, [str(qty) for qty in self.move_ids.mapped('product_uom_qty')]))
            picking_data = picking_ids.filtered(lambda p: not p.backorder_id)
            picking_bck_orders = picking_ids.filtered(lambda p: p.backorder_id)
            if picking_data:
                delivery_date = ['Delivery date: '+str(picking.scheduled_date)[0:10]+' ['+qty_dict[picking.id]+' pcs]' for picking in picking_data if picking.state == 'done' and picking.scheduled_date]
                res.update({'delivery_date':delivery_date})

                expected_date = ['Expected date: '+str(picking.scheduled_date)[0:10]+' ['+qty_dict[picking.id]+' pcs]' for picking in picking_data if picking.state in ['confirmed', 'assigned'] and picking.scheduled_date]
                res.update({'expected_date':expected_date})

            if picking_bck_orders:
                done_back_order_ref = ['Backorder: '+bo.name+' ('+str(bo.scheduled_date)[0:10]+')'+' ['+qty_dict[bo.id]+' pcs]' for bo in picking_bck_orders if bo.state == 'done' and bo.scheduled_date]
                res.update({'done_back_ref':done_back_order_ref})

                back_order_ref = ['Backorder: '+bo.name+' ['+qty_dict[bo.id]+' pcs]' for bo in picking_bck_orders if bo.state != 'done']
                res.update({'back_ref':back_order_ref})
        return res