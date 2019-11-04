# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = "res.company"

    intercompany_id = fields.Many2one('res.company',
        string='Intercompany Customer/Supplier Invoice Received From',
        help="Intercompany Customer/Supplier invoice received from company A to company B.")

    all_customer_accounts = fields.Boolean(string='For all customer invoices & credit notes (Y/N).')
    all_vendor_accounts = fields.Boolean(string='For all vendor bills & debit notes (Y/N).')
    auto_validate = fields.Boolean(string='Auto validate customer/supplier invoices (Y/N).')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        # ('paid', 'Paid'),
        # ('cancel', 'Cancelled'),
    ], string='Invoice Status',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

