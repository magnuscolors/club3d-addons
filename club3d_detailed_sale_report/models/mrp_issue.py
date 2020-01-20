# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class StockMRPIssueWIZ(models.TransientModel):
    _name = 'stock.mrp.issue.wiz'
    _description = 'MRP Issue'


    def open_table(self):
        self.ensure_one()
        location_ids = self.env.user.company_id.delivery_warehouse_id.view_location_id.child_ids.ids
        op, ids = ('IN', tuple(location_ids)) if len(location_ids) > 1 else ('=', location_ids[0])

        delete_query = (""" DELETE FROM stock_mrp_issue""")
        self.env.cr.execute(delete_query)

        list_query = ("""                      
                  SELECT DISTINCT product_id FROM (		
                        (SELECT id, product_id, date_expected, product_type, on_hand, move_quantity, SUM(move_quantity) OVER (PARTITION BY product_id ORDER BY date_expected, id)+on_hand AS cum_sum1 FROM 
                            (SELECT
                                sm.id as id,
                                sm.product_id as product_id,
                                sm.date_expected as date_expected,
                                (SELECT type FROM product_template WHERE id = (SELECT product_tmpl_id FROM product_product WHERE id = sm.product_id)) AS product_type,
                                CASE
                                  WHEN (SELECT SUM(quantity) FROM stock_quant WHERE product_id = sm.product_id AND location_id {0} {1}) IS NOT NULL
                                  THEN
                                    (SELECT SUM(quantity) FROM stock_quant WHERE product_id = sm.product_id AND location_id {0} {1})
                                  ELSE
                                     0
                                  END AS on_hand,
                                CASE
                                  WHEN (SELECT id FROM stock_location WHERE usage IN ('customer', 'inventory') AND id = sm.location_dest_id) IS NOT NULL
                                  THEN
                                    -sm.product_uom_qty
                                  ELSE
                                     sm.product_uom_qty
                                  END AS move_quantity
                                FROM stock_move sm WHERE sm.state NOT IN ('cancel', 'done') AND (sm.location_dest_id {0} {1} OR sm.location_id {0} {1}) ORDER BY sm.product_id, sm.date_expected
                            ) temp1
                        ) 
                    ) temp2 WHERE cum_sum1 < 0 AND product_type = 'product'
            """.format(op, ids))

        self.env.cr.execute(list_query)
        res = self.env.cr.fetchall()
        stock_mrp_issue = self.env['stock.mrp.issue']
        for dt in res:
            stock_mrp_issue.create({'product_id':dt[0]})
        action_name = 'club3d_detailed_sale_report.action_stock_mrp_issue'
        tree_view_name = 'club3d_detailed_sale_report.view_stock_mrp_issue_tree'

        action = self.env.ref(action_name)
        result = action.read()[0]
        tree_view = self.env.ref(tree_view_name)
        result['views'] = [(tree_view.id, 'tree')]
        return result

class StockMRPIssue(models.Model):
    _name = 'stock.mrp.issue'

    product_id = fields.Many2one('product.product', string='Product',)

    @api.multi
    def action_open_ref(self):
        self.ensure_one()
        domain = {
            'name': self.product_id.name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.product_id.id,
            'res_model': 'product.product',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        return domain