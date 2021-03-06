# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import api, fields, models, registry, _
from odoo.tools import float_compare, float_round, float_is_zero, pycompat


class StockMove(models.Model):
    _inherit = "stock.move"

    def fetch_product_standard_price(self):

        pp = self.env['ir.property'].sudo().with_context(force_company=self.company_id.id).get('standard_price',
                                                                                               'product.product',
                                                                                               'product.product,%s' % self.product_id.id)
        return pp

    @api.model
    def create(self, values):
        res = super(StockMove, self).create(values)
        if res.sale_line_id and res.price_unit == 0 and res.sale_line_id.order_id.company_id != res.company_id:
            res.price_unit = self.fetch_product_standard_price()
        return res

    @api.multi
    def write(self, values):
        res = super(StockMove, self).write(values)
        for move in self:
            if move.sale_line_id and move.price_unit == 0 and move.sale_line_id.company_id != move.company_id:
                move.price_unit = self.fetch_product_standard_price()
        return res


    @api.model
    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id):
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)
        if self.picking_id.sale_id.company_id != self.company_id:
            for line in res:
                line[2]['company_id'] = self.company_id.id
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        if self.picking_id and self.picking_id.sale_id and self.picking_id.sale_id.company_id != self.picking_id.company_id:
            self.ensure_one()
            AccountMove = self.env['account.move']
            quantity = self.env.context.get('forced_quantity', self.product_qty)
            quantity = quantity if self._is_in() else -1 * quantity

            # Make an informative `ref` on the created account move to differentiate between classic
            # movements, vacuum and edition of past moves.
            ref = self.picking_id.name
            if self.env.context.get('force_valuation_amount'):
                if self.env.context.get('forced_quantity') == 0:
                    ref = 'Revaluation of %s (negative inventory)' % ref
                elif self.env.context.get('forced_quantity') is not None:
                    ref = 'Correction of %s (modification of past move)' % ref

            move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
            if move_lines:
                date = self._context.get('force_period_date', fields.Date.context_today(self))
                data = {
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': ref,
                    'stock_move_id': self.id,
                    'company_id' : self.picking_id.company_id.id
                }

                new_account_move = AccountMove.sudo().create(data)

                new_account_move.post()
        else:
            return super(StockMove, self)._create_account_move_line(credit_account_id, debit_account_id, journal_id)

    def _run_valuation(self, quantity=None):
        res = super(StockMove, self)._run_valuation(quantity)
        if self._is_out() and not self.value:
            valued_move_lines = self.move_line_ids.filtered(lambda
                                                                ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                                     self.product_id.uom_id)
            self.env['stock.move']._run_fifo(self, quantity=quantity)
            if self.product_id.cost_method in ['standard', 'average']:
                curr_rounding = self.company_id.currency_id.rounding
                unit_price = self._get_price_unit()
                value = -float_round(
                    unit_price * (valued_quantity if quantity is None else quantity),
                    precision_rounding=curr_rounding)
                self.write({
                    'value': value if quantity is None else self.value + value,
                    'price_unit': value / valued_quantity,
                })
        return res

    def fetch_company_dependent_values(self):
        sudo_prop = self.env['ir.property'].sudo().with_context(force_company=self.company_id.id)

        journal = sudo_prop.get('property_stock_journal','product.category', 'product.category,%s' % self.product_id.categ_id.id)
        journal =  journal.id if journal else journal
        if not journal:
            journal = sudo_prop.get('property_stock_journal','product.category').id

        acc_src = sudo_prop.get('property_stock_account_input_categ_id', 'product.category',
                                      'product.category,%s' % self.product_id.categ_id.id)
        acc_src = acc_src.id if acc_src else acc_src
        if not acc_src:
            acc_src = sudo_prop.get('property_stock_account_input_categ_id', 'product.category').id

        acc_dest = sudo_prop.get('property_stock_account_output_categ_id', 'product.category',
                                'product.category,%s' % self.product_id.categ_id.id)
        acc_dest = acc_dest.id if acc_dest else acc_dest
        if not acc_dest:
            acc_dest = sudo_prop.get('property_stock_account_output_categ_id', 'product.category').id

        acc_valuation = sudo_prop.get('property_stock_valuation_account_id', 'product.category',
                                    'product.category,%s' % self.product_id.categ_id.id)
        acc_valuation = acc_valuation.id if acc_valuation else acc_valuation
        if not acc_valuation:
            acc_valuation = sudo_prop.get('property_stock_valuation_account_id', 'product.category').id

        return journal, acc_src, acc_dest, acc_valuation


    @api.multi
    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation = \
            super(StockMove, self)._get_accounting_data_for_valuation()
        if self.picking_id and self.picking_id.sale_id and self.picking_id.sale_id.company_id != self.picking_id.company_id:
            journal_id, acc_src, acc_dest, acc_valuation = self.fetch_company_dependent_values()
        return journal_id, acc_src, acc_dest, acc_valuation

    @api.multi
    def product_price_update_before_done(self, forced_qty=None):
        tmpl_dict = defaultdict(lambda: 0.0)
        # adapt standard price on incomming moves if the product cost_method is 'average'
        std_price_update = {}
        for move in self.filtered(lambda move: move._is_in() and move.product_id.cost_method == 'average'):
            product_tot_qty_available = move.product_id.qty_available + tmpl_dict[move.product_id.id]
            rounding = move.product_id.uom_id.rounding

            qty_done = move.product_uom._compute_quantity(move.quantity_done, move.product_id.uom_id)
            qty = forced_qty or qty_done
            # If the current stock is negative, we should not average it with the incoming one
            if float_is_zero(product_tot_qty_available, precision_rounding=rounding) or product_tot_qty_available < 0:
                new_std_price = move._get_price_unit()
            elif float_is_zero(product_tot_qty_available + move.product_qty, precision_rounding=rounding) or \
                    float_is_zero(product_tot_qty_available + qty, precision_rounding=rounding):
                new_std_price = move._get_price_unit()
            else:
                # Get the standard price
                amount_unit = std_price_update.get((move.company_id.id, move.product_id.id)) or move.product_id.with_context(force_company=move.company_id.id).standard_price

                new_std_price = ((amount_unit * product_tot_qty_available) + (move._get_price_unit() * qty)) / (product_tot_qty_available + qty)

            tmpl_dict[move.product_id.id] += qty_done
            # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
            move.product_id.with_context(force_company=move.company_id.id).sudo().write({'standard_price': new_std_price})
            std_price_update[move.company_id.id, move.product_id.id] = new_std_price