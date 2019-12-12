# -*- coding: utf-8 -*-
from odoo import http

# class Club3dAutoFreightCostReservation(http.Controller):
#     @http.route('/club3d_auto_freight_cost_reservation/club3d_auto_freight_cost_reservation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/club3d_auto_freight_cost_reservation/club3d_auto_freight_cost_reservation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('club3d_auto_freight_cost_reservation.listing', {
#             'root': '/club3d_auto_freight_cost_reservation/club3d_auto_freight_cost_reservation',
#             'objects': http.request.env['club3d_auto_freight_cost_reservation.club3d_auto_freight_cost_reservation'].search([]),
#         })

#     @http.route('/club3d_auto_freight_cost_reservation/club3d_auto_freight_cost_reservation/objects/<model("club3d_auto_freight_cost_reservation.club3d_auto_freight_cost_reservation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('club3d_auto_freight_cost_reservation.object', {
#             'object': obj
#         })