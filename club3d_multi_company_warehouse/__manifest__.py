# -*- coding: utf-8 -*-
{
    'name': "club3d_multi_company_warehouse",

    'summary': """
        Club3d Multi-company warehouse""",

    'description': """
        Club3d Multi-company warehouse
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}