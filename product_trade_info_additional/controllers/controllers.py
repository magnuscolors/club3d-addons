# -*- coding: utf-8 -*-
from odoo import http

# class ProductTradeInfoAdditional(http.Controller):
#     @http.route('/product_trade_info_additional/product_trade_info_additional/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_trade_info_additional/product_trade_info_additional/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_trade_info_additional.listing', {
#             'root': '/product_trade_info_additional/product_trade_info_additional',
#             'objects': http.request.env['product_trade_info_additional.product_trade_info_additional'].search([]),
#         })

#     @http.route('/product_trade_info_additional/product_trade_info_additional/objects/<model("product_trade_info_additional.product_trade_info_additional"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_trade_info_additional.object', {
#             'object': obj
#         })