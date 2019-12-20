# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ReportStockMoveForecast(models.Model):
    _name = 'report.stock.move.forecast'
    _auto = False
    _order = "date"


    @api.depends('quantity')
    def _cumulative_quantity_compute(self):
        global x
        x = 0
        for move in self.search([('id', 'in', self.ids)], order="id, date"):
            cum_qty = x + move.quantity
            move.cumulative_quantity = move.product_id.qty_available + cum_qty
            x = cum_qty

    date = fields.Datetime(string='Expected Date', readonly=True)
    last_modification_date = fields.Datetime(string='Last Modification Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True,)
    qty_available = fields.Float(related='product_id.qty_available', readonly=True, store=False)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True,)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template',
                                      related='product_id.product_tmpl_id', readonly=True)
    ref_number = fields.Char(string='PO/SO Number', readonly=True)
    cumulative_quantity = fields.Float(string='Cumulative Quantity', compute='_cumulative_quantity_compute', store=False)
    quantity = fields.Float(string='Quantity', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)

    @api.multi
    def action_open_ref(self):
        self.ensure_one()
        domain = {
            'name': self.ref_number,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        if self.picking_id.sale_id:
            domain.update({
                'res_id':self.picking_id.sale_id.id,
                'res_model': 'sale.order',
                })
        elif self.picking_id.purchase_id:
            domain.update({
                'res_id': self.picking_id.purchase_id.id,
                'res_model': 'purchase.order',
            })
        return domain

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_stock_move_forecast')
        self._cr.execute("""
                CREATE or REPLACE VIEW report_stock_move_forecast AS (
                  SELECT
                      sm.id as id, 
                      sm.product_id as product_id,
                      sm.date_expected as date,
                      sm.write_date as last_modification_date,
                      CASE 
                          WHEN (SELECT id FROM stock_location WHERE usage IN ('customer', 'inventory') AND id = sm.location_dest_id) IS NOT NULL
                          THEN
                            -sm.product_uom_qty
                          ELSE 
                             sm.product_uom_qty
                          END as quantity,
                      sm.origin as ref_number,
                      sm.partner_id as partner_id,
                      sm.picking_id as picking_id
                  FROM stock_move sm
                  WHERE sm.state NOT IN ('cancel', 'done')
                  ORDER BY sm.date_expected
                )""")