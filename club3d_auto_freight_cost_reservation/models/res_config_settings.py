# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_default_freight_product(self):
        return self.env.ref('club3d_auto_freight_cost_reservation.product_product_freight').id

    def _get_default_account_domain(self):
        return [('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', self.env.user.company_id.id)]

    freight_cost_account = fields.Many2one(
        'account.account', 'Freight Cost Account',
        domain=lambda self: self._get_default_account_domain(),
        help="Freight Cost/Debit Account.")

    freight_reservation_account = fields.Many2one(
        'account.account', 'Freight Reservation Account',
        domain=lambda self: self._get_default_account_domain(),
        help="Freight Reservation/Credit Account.")

    freight_product = fields.Many2one('product.product',
        string='Freight Product',
        help="Freight product for journal entries.",
        default = _get_default_freight_product,
        domain=[('type', '=', 'service')]
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        freight_cost_account = IrDefault.get('res.company', "freight_cost_account", company_id=self.company_id.id or self.env.user.company_id.id)
        freight_reservation_account = IrDefault.get('res.company', "freight_reservation_account",
                                             company_id=self.company_id.id or self.env.user.company_id.id)
        freight_product = IrDefault.get('res.company', "freight_product",
                                                    company_id=self.company_id.id or self.env.user.company_id.id)
        res.update(
            freight_cost_account=freight_cost_account if freight_cost_account else False,
            freight_reservation_account=freight_reservation_account if freight_reservation_account else False,
            freight_product=freight_product if freight_product else False,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.company', "freight_cost_account", self.freight_cost_account.id, company_id=self.company_id.id)
        IrDefault.set('res.company', "freight_reservation_account", self.freight_reservation_account.id, company_id=self.company_id.id)
        IrDefault.set('res.company', "freight_product", self.freight_product.id, company_id=self.company_id.id)