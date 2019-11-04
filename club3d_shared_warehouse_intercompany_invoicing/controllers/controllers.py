# -*- coding: utf-8 -*-
from odoo import http

# class Club3dSharedWarehouseIntercompanyInvoicing(http.Controller):
#     @http.route('/club3d_shared_warehouse_intercompany_invoicing/club3d_shared_warehouse_intercompany_invoicing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/club3d_shared_warehouse_intercompany_invoicing/club3d_shared_warehouse_intercompany_invoicing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('club3d_shared_warehouse_intercompany_invoicing.listing', {
#             'root': '/club3d_shared_warehouse_intercompany_invoicing/club3d_shared_warehouse_intercompany_invoicing',
#             'objects': http.request.env['club3d_shared_warehouse_intercompany_invoicing.club3d_shared_warehouse_intercompany_invoicing'].search([]),
#         })

#     @http.route('/club3d_shared_warehouse_intercompany_invoicing/club3d_shared_warehouse_intercompany_invoicing/objects/<model("club3d_shared_warehouse_intercompany_invoicing.club3d_shared_warehouse_intercompany_invoicing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('club3d_shared_warehouse_intercompany_invoicing.object', {
#             'object': obj
#         })