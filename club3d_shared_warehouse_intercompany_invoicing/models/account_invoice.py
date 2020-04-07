# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    inter_company_invoice = fields.Many2one('account.invoice', string='Intercompany Invoice', help='Intercompnay auto created customer/supplier invoices', index=True)

    def _prepare_supplier_line_from_invoice_line(self, line):
        taxes = line.product_id.supplier_taxes_id
        invoice_line_tax_ids = line.invoice_id.fiscal_position_id.map_tax(taxes, line.product_id, self.partner_id)
        invoice_line = self.env['account.invoice.line']
        data = {
            'name': line.name,
            'origin': line.origin,
            'uom_id': line.uom_id.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            # 'analytic_tag_ids': [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids],
            # 'invoice_line_tax_ids': [(4, tax.id, None) for tax in line.invoice_line_tax_ids],
        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.invoice_id.fiscal_position_id,
                                                        self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        new_line = self.env['account.invoice.line'].new(data)
        new_line.analytic_tag_ids = line.analytic_tag_ids.ids
        new_line.invoice_line_tax_ids = invoice_line_tax_ids.ids
        return new_line

    @api.multi
    def check_intercompany_settings(self, state):
        IrDefault = self.env['ir.default'].sudo()
        inv_state = IrDefault.get('res.company', "state", company_id=self.company_id.id)
        intercompany_id = IrDefault.get('res.company', "intercompany_id", company_id=self.company_id.id)

        if self.type == 'out_invoice':
            intercompany = self.env['res.company'].browse(intercompany_id)
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            po_journal_id = self.env['account.journal'].search(journal_domain, limit=1)

            account_domain = [('company_id', '=', self.company_id.id), ('internal_type', '=', 'payable'), ('deprecated', '=', False)]
            po_account = self.env['account.account'].search(account_domain, limit=1)

            all_customer_accounts = IrDefault.get('res.company', "all_customer_accounts", company_id=self.company_id.id)
            if all_customer_accounts and inv_state == state and self.company_id.id != intercompany_id:
                fiscal_position = self.env['account.fiscal.position'].get_fiscal_position(intercompany.partner_id.id,delivery_id=intercompany.partner_id.address_get(['delivery'])['delivery'])

                vendor_inv = self.copy(default={'partner_id':intercompany.partner_id.id,
                                   'type':'in_invoice', 'inter_company_invoice':self.id,
                                   'journal_id':po_journal_id.id,
                                   'account_id': po_account.id, 'invoice_line_ids':[],
                                    'tax_line_ids':[], 'fiscal_position_id' : fiscal_position,
                                    'name':self.number or self.name, 'date_invoice':self.date_invoice})

                new_lines = self.env['account.invoice.line']
                for line in self.invoice_line_ids:
                    new_line = vendor_inv._prepare_supplier_line_from_invoice_line(line)
                    # new_line = new_lines.new(data)
                    # new_line._set_additional_fields(vendor_inv)
                    new_lines += new_line
                vendor_inv.invoice_line_ids = new_lines

                #group taxes added to tax lines
                taxes_grouped = vendor_inv.get_taxes_values()
                tax_lines = vendor_inv.tax_line_ids.filtered('manual')
                for tax in taxes_grouped.values():
                    tax_lines += tax_lines.new(tax)
                vendor_inv.tax_line_ids = tax_lines

                auto_validate = IrDefault.get('res.company', "auto_validate", company_id=self.company_id.id)
                if auto_validate:
                    vendor_inv.action_invoice_open()
        return True

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if vals.get('state', False):
            for inv in self:
                if inv.type in ('out_invoice') and inv.invoice_line_ids:
                # if inv.type in ('out_invoice', 'out_refund') and inv.invoice_line_ids:
                    inv.check_intercompany_settings(vals['state'])
        return res

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('state', False):
            if res.type in ('out_invoice') and res.invoice_line_ids:
            # if res.type in ('out_invoice', 'out_refund') and res.invoice_line_ids:
                res.check_intercompany_settings(vals['state'])
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _prepare_invoice_line_data(self, dest_invoice, dest_company):
        vals = super(AccountInvoiceLine, self)._prepare_invoice_line_data(dest_invoice, dest_company)
        sudo_prop = self.env['ir.property'].sudo().with_context(force_company=dest_company.id)
        standard_price = sudo_prop.get('standard_price', 'product.product', 'product.product,%s' % self.product_id.id)
        if self.invoice_id.currency_id != dest_company.currency_id:
            standard_price *= self.invoice_id.currency_id.rate
        if standard_price:
            vals.update({'purchase_price':standard_price})
        if not 'uom_id' in vals:
            vals.update({'uom_id':self.uom_id.id})
        return vals
