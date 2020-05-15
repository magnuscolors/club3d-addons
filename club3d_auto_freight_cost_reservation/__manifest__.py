# -*- coding: utf-8 -*-
{
    'name': "club3d_auto_freight_cost_reservation",

    'summary': """
        Automatic freight cost reservation""",

    'description': """
        Automatic freight cost reservation
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock','delivery'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/freight_data.xml',
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}