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
                    pro_fields = pro_fields[0]
                    pro_fields.attrib['string'] = 'Customer Product Name'
                    result['arch'] = etree.tostring(partner_xml)
                pro_code_fields = partner_xml.xpath("//field[@name='product_code']")
                if pro_code_fields:
                    pro_code_fields = pro_code_fields[0]
                    pro_code_fields.attrib['string'] = 'Customer Product Code'
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