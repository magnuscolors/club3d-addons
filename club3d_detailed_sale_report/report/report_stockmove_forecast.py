# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ReportStockMoveForecast(models.Model):
    _name = 'report.stock.move.forecast'
    _auto = False


    @api.depends('quantity')
    def _cumulative_quantity_compute(self):
        global x
        x = 0
        for move in self:
            cum_qty = x + move.quantity
            move.cumulative_quantity = cum_qty
            x = cum_qty

    date = fields.Date(string='Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True, )
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True,)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template',
                                      related='product_id.product_tmpl_id', readonly=True)
    ref_number = fields.Char(string='PO/SO Number', readonly=True)
    cumulative_quantity = fields.Float(string='Cumulative Quantity', compute='_cumulative_quantity_compute', store=False)
    quantity = fields.Float(string='Quantity', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_stock_move_forecast')
        self._cr.execute("""
            CREATE or REPLACE VIEW report_stock_move_forecast AS (
                  SELECT
                      sml.id as id, 
                      sml.product_id as product_id,
                      date_trunc('week', to_date(to_char(sml.date, 'YYYY/MM/DD'), 'YYYY/MM/DD')) as date,
                      CASE 
                          WHEN (SELECT id FROM stock_location WHERE usage IN ('customer', 'inventory') AND id = sm.location_dest_id) IS NOT NULL
                          THEN
                            -sm.product_uom_qty
                          ELSE 
                             sm.product_uom_qty
                          END as quantity,
                      sm.origin as ref_number,
                      sm.partner_id as partner_id
                  FROM stock_move_line sml, stock_move sm
                  WHERE sml.move_id = sm.id
                  ORDER BY sml.id, sml.date
                )""")

