# -*- coding: utf-8 -*-
from odoo import http

# class Club3dDetailedSaleReport(http.Controller):
#     @http.route('/club3d_detailed_sale_report/club3d_detailed_sale_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/club3d_detailed_sale_report/club3d_detailed_sale_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('club3d_detailed_sale_report.listing', {
#             'root': '/club3d_detailed_sale_report/club3d_detailed_sale_report',
#             'objects': http.request.env['club3d_detailed_sale_report.club3d_detailed_sale_report'].search([]),
#         })

#     @http.route('/club3d_detailed_sale_report/club3d_detailed_sale_report/objects/<model("club3d_detailed_sale_report.club3d_detailed_sale_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('club3d_detailed_sale_report.object', {
#             'object': obj
#         })