# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], related='invoice_id.state', string='Invoice Status', index=True, readonly=True, store=True, default='draft', copy=False)