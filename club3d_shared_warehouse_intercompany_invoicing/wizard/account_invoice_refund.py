# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    """Credit Notes"""

    _inherit = "account.invoice.refund"

    @api.multi
    def intercompany_credit_note(self):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        IrDefault = self.env['ir.default'].sudo()
        company = self.env.user.company_id
        # inv_state = IrDefault.get('res.company', "state", company_id=company.id)
        # intercompany_id = IrDefault.get('res.company', "intercompany_id", company_id=company.id)
        all_customer_accounts = IrDefault.get('res.company', "all_customer_accounts", company_id=company.id)
        if all_customer_accounts:
            vendor_bills = inv_obj.search([('inter_company_invoice', 'in', context.get('active_ids'))])
            data_refund = self.read(['filter_refund'])[0]['filter_refund']
            self.with_context(active_ids=vendor_bills.ids).compute_refund(data_refund)


    @api.multi
    def invoice_refund(self):
        res = super(AccountInvoiceRefund, self).invoice_refund()
        self.intercompany_credit_note()
        return res
