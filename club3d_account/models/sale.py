# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

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

