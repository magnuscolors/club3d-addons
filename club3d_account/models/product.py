# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from lxml import etree

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form', toolbar=False,
            submenu=False):

        result = super(ProductSupplierinfo, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        type = self._context.get('default_supplierinfo_type', False)
        if view_type == 'form' and type:
            if type == 'customer':
                partner_xml = etree.XML(result['arch'])
                partner_fields = partner_xml.xpath("//field[@name='name']")
                if partner_fields:
                    partner_field = partner_fields[0]
                    partner_field.attrib['string'] = 'Customer'
                    result['arch'] = etree.tostring(partner_xml)
                pro_fields = partner_xml.xpath("//field[@name='product_name']")
                if pro_fields:
                    pro_field = pro_fields[0]
                    pro_field.attrib['string'] = 'Customer Product Name'
                    result['arch'] = etree.tostring(partner_xml)
                pro_code_fields = partner_xml.xpath("//field[@name='product_code']")
                if pro_code_fields:
                    pro_code_field = pro_code_fields[0]
                    pro_code_field.attrib['string'] = 'Customer Product Code'
                    result['arch'] = etree.tostring(partner_xml)

        elif view_type == 'tree' and type:
            if type == 'customer':
                partner_xml = etree.XML(result['arch'])
                partner_fields = partner_xml.xpath("//field[@name='name']")
                if partner_fields:
                    partner_field = partner_fields[0]
                    partner_field.attrib['string'] = 'Customer'
                    result['arch'] = etree.tostring(partner_xml)

        return result



class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.multi
    def name_get(self):
        res = super(ProductProduct, self).name_get()

        def _update_name_get(alist, key, value):
            return [(k, v) if (k != key) else (key, value) for (k, v) in alist]

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids
        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            for product in supplier_info.mapped('product_tmpl_id').sudo():
                res = _update_name_get(res, product.id,  '[%s] %s' % (product.default_code,product.name))
        return res