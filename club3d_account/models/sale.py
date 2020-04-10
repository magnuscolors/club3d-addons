# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_domain(self):
        data = {}
        if self.partner_id:
            invoice_add = [self.partner_id.id] + self.partner_id.search([('parent_id', '=', self.partner_id.id),('type', '=', 'invoice')]).ids
            delivery_add = [self.partner_id.id] + self.partner_id.search([('parent_id', '=', self.partner_id.id), ('type', '=', 'delivery')]).ids
            data = {'partner_invoice_id': [('id', 'in', invoice_add)],
                    'partner_shipping_id': [('id', 'in', delivery_add)]}
        return {'domain': data}

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        """
        get supplier info product code and name append with sale description
        :return:
        """
        result = super(SaleOrderLine, self).product_id_change()
        product = self.product_id

        if not product and not self.order_id.partner_id:
            return result

        vals = {}
        product_template_ids = product.sudo().mapped('product_tmpl_id').ids
        supplier_info = self.env['product.supplierinfo'].sudo().search([
            ('product_tmpl_id', 'in', product_template_ids),
            ('name', '=', self.order_id.partner_id.id),
        ], limit=1)
        if supplier_info:
            name = ''
            if supplier_info.product_code:
                name += '[%s] ' % (supplier_info.product_code)
            if supplier_info.product_name:
                name += '%s' % (supplier_info.product_name)
            name = product.name if not name else name
            if product.description_sale:
                name += '\n' + product.description_sale
            vals['name'] = name
        self.update(vals)

        return result

