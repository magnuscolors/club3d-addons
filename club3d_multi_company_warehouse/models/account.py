# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, _

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if move.stock_move_id and move.company_id != move.stock_move_id.company_id:
            move.company_id = move.stock_move_id.company_id.id
            move.line_ids.write({'company_id':move.stock_move_id.company_id.id})
        return move
