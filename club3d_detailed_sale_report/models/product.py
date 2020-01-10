from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
import operator as py_operator

class Product(models.Model):
    _inherit = "product.product"

    default_virtual_available = fields.Float('Default Warehouse Forecast Quantity', compute='_def_compute_quantities')
    default_qty_available = fields.Float('Default Quantity On Hand', compute='_def_compute_quantities')
    default_incoming_qty = fields.Float('Default Incoming', compute='_def_compute_quantities', )
    default_outgoing_qty = fields.Float('Default Outgoing', compute='_def_compute_quantities')

    @api.depends('qty_available', 'incoming_qty', 'outgoing_qty', 'virtual_available')
    def _def_compute_quantities(self):
        ctx = self.env.context.copy()
        warehouse = self.env.user.company_id.delivery_warehouse_id
        ctx.update({'warehouse': warehouse.id})
        for product in self:
            product_dic = self.with_context(ctx)._product_available()
            product.default_qty_available = product_dic[product.id]["qty_available"]
            product.default_incoming_qty = product_dic[product.id]["incoming_qty"]
            product.default_outgoing_qty = product_dic[product.id]["outgoing_qty"]
            product.default_virtual_available = product_dic[product.id]["virtual_available"]

class Product(models.Model):
    _inherit = "product.template"

    default_virtual_available = fields.Float('Default Warehouse Forecast Quantity', compute='_def_compute_quantities')
    default_qty_available = fields.Float('Default Quantity On Hand', compute='_def_compute_quantities')
    default_incoming_qty = fields.Float('Default Incoming', compute='_def_compute_quantities',)
    default_outgoing_qty = fields.Float('Default Outgoing', compute='_def_compute_quantities')

    @api.depends('qty_available', 'incoming_qty', 'outgoing_qty', 'virtual_available')
    def _def_compute_quantities(self):
        res = self._def_compute_quantities_dict()
        for template in self:
            template.default_qty_available = res[template.id]['qty_available']
            template.default_incoming_qty = res[template.id]['incoming_qty']
            template.default_outgoing_qty = res[template.id]['outgoing_qty']
            template.default_virtual_available = res[template.id]['virtual_available']

    def _def_compute_quantities_dict(self):
        ctx = self.env.context.copy()
        warehouse = self.env.user.company_id.delivery_warehouse_id
        ctx.update({'location': warehouse.view_location_id.id})
        variants_available = self.with_context(ctx).mapped('product_variant_ids')._product_available()
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
            }
        return prod_available
