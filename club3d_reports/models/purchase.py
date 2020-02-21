# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(PurchaseOrderLine, self).onchange_product_id()
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