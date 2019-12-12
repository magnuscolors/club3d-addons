# -*- coding: utf-8 -*-
from odoo import http

# class Club3dReports(http.Controller):
#     @http.route('/club3d_reports/club3d_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/club3d_reports/club3d_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('club3d_reports.listing', {
#             'root': '/club3d_reports/club3d_reports',
#             'objects': http.request.env['club3d_reports.club3d_reports'].search([]),
#         })

#     @http.route('/club3d_reports/club3d_reports/objects/<model("club3d_reports.club3d_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('club3d_reports.object', {
#             'object': obj
#         })