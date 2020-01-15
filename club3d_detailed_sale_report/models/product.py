from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class Product(models.Model):
    _inherit = "product.product"

    default_virtual_available = fields.Float('Def. WH Forecast Quantity', compute='_def_compute_quantities',search='_search_default_virtual_available', digits=dp.get_precision('Product Unit of Measure'))
    default_qty_available = fields.Float('Def. WH Quantity On Hand', compute='_def_compute_quantities', search='_search_default_qty_available', digits=dp.get_precision('Product Unit of Measure'))
    default_incoming_qty = fields.Float('Def. WH Incoming', compute='_def_compute_quantities', search='_search_default_incoming_qty', digits=dp.get_precision('Product Unit of Measure'))
    default_outgoing_qty = fields.Float('Def. WH Outgoing', compute='_def_compute_quantities', search='_search_default_outgoing_qty', digits=dp.get_precision('Product Unit of Measure'))
    def_wh_atp = fields.Boolean('Def. WH ATP', compute='_def_wh_atp_compute', search='_search_wh_atp')

    def _get_apt_cal(self):
        product_ids = []
        for product in self:
            out_qty, in_qty = 0.0, 0.0
            domain = [
                ('product_id', '=', product.id),
                ('state', 'not in', ('cancel', 'done')),
            ]
            out_domain = domain + [('location_dest_id.usage', 'in', ('customer', 'inventory'))]
            in_domain = domain
            Move = self.env['stock.move']
            warehouse = self.env.user.company_id.delivery_warehouse_id
            location_ids = warehouse.view_location_id.child_ids.ids
            if location_ids:
                out_domain += [
                    ('location_id', 'in', location_ids),
                ]
                in_domain += [('location_dest_id', 'in', location_ids)]

            latest_date_expected = Move.search(out_domain, order='date_expected Desc', limit=1).date_expected
            if not latest_date_expected:
                continue
            out_moves = Move.read_group(out_domain, ['product_id', 'product_qty'], ['product_id'])
            if out_moves:
                out_qty = out_moves and out_moves[0]['product_qty']

            if latest_date_expected:
                in_domain += [('date_expected', '<=', latest_date_expected)]

            in_moves = Move.read_group(in_domain, ['product_id', 'product_qty'], ['product_id'])
            if in_moves:
                in_qty = in_moves and in_moves[0]['product_qty']

            forecasted_qty = product.default_incoming_qty + in_qty - out_qty
            if forecasted_qty < 0:
                product_ids.append(product.id)
        return product_ids
        
        
    @api.depends('qty_available', 'incoming_qty', 'outgoing_qty', 'virtual_available', 'stock_move_ids.date_expected')
    def _def_wh_atp_compute(self):
        product_ids = self._get_apt_cal()
        for product in self:
            if product.id in product_ids:
                product.def_wh_atp = True
            else:
                product.def_wh_atp = False

    def _search_wh_atp(self, operator, value):
        product_ids = self.search([])._get_apt_cal()
        if operator == '=':
            return [('id', 'in', product_ids)]
        else:
            return [('id', 'in', self.search([('id', 'not in', product_ids)]).ids)]

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

    def _search_default_qty_available(self, operator, value):
        # In the very specific case we want to retrieve products with stock available, we only need
        # to use the quants, not the stock moves. Therefore, we bypass the usual
        # '_search_product_quantity' method and call '_def_search_qty_available_new' instead. This
        # allows better performances.
        if value == 0.0 and operator == '>' and not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self._def_search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
            return [('id', 'in', product_ids)]
        return self._def_search_product_quantity(operator, value, 'default_qty_available')

    def _search_default_virtual_available(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._def_search_product_quantity(operator, value, 'default_virtual_available')

    def _search_default_incoming_qty(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._def_search_product_quantity(operator, value, 'default_incoming_qty')

    def _search_default_outgoing_qty(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._def_search_product_quantity(operator, value, 'default_outgoing_qty')

    def _def_search_product_quantity(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ('default_qty_available', 'default_virtual_available', 'default_incoming_qty', 'default_outgoing_qty'):
            raise UserError(_('Invalid domain left operand %s') % field)
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name which slows
        # down the search because of the join on the translation table to get the translated names.
        for product in self.with_context(prefetch_fields=False).search([], order='id'):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [('id', 'in', ids)]

    def _def_search_qty_available_new(self, operator, value, lot_id=False, owner_id=False, package_id=False):
        ''' Optimized method which doesn't search on stock.moves, only on stock.quants. '''
        product_ids = set()
        ctx = self.env.context.copy()
        warehouse = self.env.user.company_id.delivery_warehouse_id
        ctx.update({'warehouse': warehouse.id})
        domain_quant = self.with_context(ctx)._get_domain_locations()[0]
        if lot_id:
            domain_quant.append(('lot_id', '=', lot_id))
        if owner_id:
            domain_quant.append(('owner_id', '=', owner_id))
        if package_id:
            domain_quant.append(('package_id', '=', package_id))

        quants_groupby = self.env['stock.quant'].read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id')
        for quant in quants_groupby:
            if OPERATORS[operator](quant['quantity'], value):
                product_ids.add(quant['product_id'][0])
        return list(product_ids)

class Product(models.Model):
    _inherit = "product.template"

    default_virtual_available = fields.Float('Def. WH Forecast Quantity', compute='_def_compute_quantities', search='_search_default_virtual_available',
        digits=dp.get_precision('Product Unit of Measure'))
    default_qty_available = fields.Float('Def. WH Quantity On Hand', compute='_def_compute_quantities', search='_search_default_qty_available',
        digits=dp.get_precision('Product Unit of Measure'))
    default_incoming_qty = fields.Float('Def. WH Incoming', compute='_def_compute_quantities', search='_search_default_incoming_qty',
        digits=dp.get_precision('Product Unit of Measure'))
    default_outgoing_qty = fields.Float('Def. WH Outgoing', compute='_def_compute_quantities', search='_search_default_outgoing_qty',
        digits=dp.get_precision('Product Unit of Measure'))
    # def_wh_atp = fields.Boolean('Def. WH ATP', compute='_def_wh_atp_compute', search='_search_wh_atp')

    # @api.depends('qty_available', 'incoming_qty', 'outgoing_qty', 'virtual_available')
    # def _def_wh_atp_compute(self):
    #     for template in self:
    #         atp_variants = template.mapped('product_variant_ids')._get_apt_cal()
    #         print ('------atp_variants-----',atp_variants)
    #         if atp_variants:
    #             template.def_wh_atp = True
    #         else:
    #             template.def_wh_atp = False

    # def _search_wh_atp(self, operator, value):
    #     product_ids = self.search([])._get_apt_cal()
    #     if operator == '=':
    #         return [('id', 'in', product_ids)]
    #     else:
    #         return [('id', 'in', self.search([('id', 'not in', product_ids)]).ids)]

    # def _def_wh_atp_compute_dict(self):
    #     prod_available = {}
    #     for template in self:
    #         atp = False
    #         atp_variants = template.mapped('product_variant_ids')._get_apt_cal()
    #         if atp_variants:
    #             atp = True
    #         prod_available[template.id] = atp
    #     return prod_available

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

    def _search_default_qty_available(self, operator, value):
        domain = [('default_qty_available', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]

    def _search_default_virtual_available(self, operator, value):
        domain = [('default_virtual_available', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]

    def _search_default_incoming_qty(self, operator, value):
        domain = [('default_incoming_qty', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]

    def _search_default_outgoing_qty(self, operator, value):
        domain = [('default_outgoing_qty', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]
