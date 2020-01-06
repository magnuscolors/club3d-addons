# -*- coding: utf-8 -*-
{
    'name': "club3d_detailed_sale_report",

    'summary': """
        Multiple reports & layouts Club3D""",

    'description': """
        Multiple reports & layouts Club3D
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'stock', 'account', 'club3d_multi_company_warehouse'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/report_stockmove_forecast.xml',
        'views/sale_views.xml',
        'views/invoice_views.xml',
        'views/stock_views.xml',
        'views/product_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}