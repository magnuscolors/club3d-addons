# -*- coding: utf-8 -*-
from odoo import http

# class Club3dMultiCompanyWarehouse(http.Controller):
#     @http.route('/club3d_multi_company_warehouse/club3d_multi_company_warehouse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/club3d_multi_company_warehouse/club3d_multi_company_warehouse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('club3d_multi_company_warehouse.listing', {
#             'root': '/club3d_multi_company_warehouse/club3d_multi_company_warehouse',
#             'objects': http.request.env['club3d_multi_company_warehouse.club3d_multi_company_warehouse'].search([]),
#         })

#     @http.route('/club3d_multi_company_warehouse/club3d_multi_company_warehouse/objects/<model("club3d_multi_company_warehouse.club3d_multi_company_warehouse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('club3d_multi_company_warehouse.object', {
#             'object': obj
#         })