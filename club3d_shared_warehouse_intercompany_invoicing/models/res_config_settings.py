# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_default_company_domain(self):
        return [('id', '!=', self.env.user.company_id.id)]

    intercompany_id = fields.Many2one('res.company',
        string='Intercompany Customer/Supplier Invoice Received From',
        help="Intercompany Customer/Supplier invoice received from company A to company B.", domain=lambda self: self._get_default_company_domain())

    all_customer_accounts = fields.Boolean(string='For all customer invoices & credit notes (Y/N).')
    all_vendor_accounts = fields.Boolean(string='For all vendor bills & debit notes (Y/N).')
    auto_validate = fields.Boolean(string='Auto validate customer/supplier invoices (Y/N).')

    state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Open'),
            # ('paid', 'Paid'),
            # ('cancel', 'Cancelled'),
        ], string='Invoice Status',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        intercompany_id = IrDefault.get('res.company', "intercompany_id", company_id=self.company_id.id or self.env.user.company_id.id)
        all_customer_accounts = IrDefault.get('res.company', "all_customer_accounts", company_id=self.company_id.id or self.env.user.company_id.id)
        auto_validate = IrDefault.get('res.company', "auto_validate", company_id=self.company_id.id or self.env.user.company_id.id)
        all_vendor_accounts = IrDefault.get('res.company', "all_vendor_accounts", company_id=self.company_id.id or self.env.user.company_id.id)
        state = IrDefault.get('res.company', "state", company_id=self.company_id.id or self.env.user.company_id.id)
        res.update(
            intercompany_id=intercompany_id if intercompany_id else False,
            all_customer_accounts=all_customer_accounts,
            all_vendor_accounts=all_vendor_accounts,
            auto_validate=auto_validate,
            state=state,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.company', "intercompany_id", self.intercompany_id.id, company_id=self.company_id.id)
        IrDefault.set('res.company', "all_customer_accounts", self.all_customer_accounts, company_id=self.company_id.id)
        IrDefault.set('res.company', "all_vendor_accounts", self.all_vendor_accounts, company_id=self.company_id.id)
        IrDefault.set('res.company', "auto_validate", self.auto_validate, company_id=self.company_id.id)
        IrDefault.set('res.company', "state", self.state, company_id=self.company_id.id)
