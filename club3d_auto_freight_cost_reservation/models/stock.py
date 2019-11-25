# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, _
from odoo.tools import float_compare, float_round, float_is_zero, pycompat
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_freight_account_move_line(self, qty, cost, credit_account_id, debit_account_id, freight_product, ref):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        valuation_amount = (cost * freight_product.product_tmpl_id.categ_id.debit_freight_percentage)/100

        debit_value = self.company_id.currency_id.round(valuation_amount)

        credit_value = debit_value

        partner_id = (self.picking_id.partner_id and self.env['res.partner']._find_accounting_partner(self.picking_id.partner_id).id) or False
        debit_line_vals = {
            'name': freight_product.name,
            'product_id': freight_product.id,
            'quantity': qty,
            'product_uom_id': freight_product.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            'stock_move_id': self.id,
        }
        credit_line_vals = {
            'name': freight_product.name,
            'product_id': freight_product.id,
            'quantity': qty,
            'product_uom_id': freight_product.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
            'stock_move_id': self.id,
        }
        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res


    def _create_freight_account_move_line(self, credit_account_id, debit_account_id, journal_id, freight_product):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.product_qty

        carrier_ref = self.picking_id.carrier_tracking_ref
        carrier_ref = ' (' + carrier_ref + ')' if carrier_ref else False
        ref = 'FCR of %s %s' % (self.picking_id.name, carrier_ref if carrier_ref else '')

        cost = self.value if self.value else self.price_unit * self.quantity_done

        move_lines = self._prepare_freight_account_move_line(quantity, abs(cost), credit_account_id, debit_account_id, freight_product, ref)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
            })
            new_account_move.post()
    
    def _action_done(self):
        res = super(StockMove, self)._action_done()
        IrDefault = self.env['ir.default'].sudo()
        for move in res:
            freight_product = IrDefault.get('res.company', "freight_product", company_id=move.company_id.id)
            freight_product = self.env['product.product'].sudo().browse(freight_product)

            if not freight_product.categ_id.automate_freight_cal:
                continue

            accounts_data = freight_product.product_tmpl_id.get_product_accounts()
            journal_id = accounts_data['stock_journal'].id

            freight_cost_account = IrDefault.get('res.company', "freight_cost_account", company_id=move.company_id.id)
            freight_reservation_account = IrDefault.get('res.company', "freight_reservation_account", company_id=move.company_id.id)

        # for move in res:
            company_to = move._is_in() and move.mapped('move_line_ids.location_dest_id.company_id') or False
            if move._is_in():
                if move.location_id and move.location_id.usage != 'customer':
                    move.with_context(force_company=company_to.id)._create_freight_account_move_line(freight_reservation_account, freight_cost_account, journal_id, freight_product)
        return res

