# -*- coding: utf-8 -*-
{
    'name': "club3d_reports",

    'summary': """
        PDF Layouts Club3D SO/PO/WH-out/Invoice""",

    'description': """
        PDF Layouts Club3D SO/PO/WH-out/Invoice
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        'report/sale_report_templates.xml',
        'report/report_deliveryslip.xml',
        'report/report_invoice.xml',
        'views/res_company_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}