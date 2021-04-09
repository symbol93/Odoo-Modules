from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    on_custody = fields.Boolean(string="Sale on custody", track_visibility='onchange', default=False, states={'open': [('readonly', False)]})

    def action_done(self):
        rez = super(StockPicking, self).action_done()
        for picking in self:
            if picking.picking_type_id.code in ['outgoing', 'incoming'] and picking.on_custody:
                picking.mapped('move_lines').action_set_custody()
        return rez


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.group_id.sale_id:
            if self.group_id.sale_id.on_custody:
                vals['on_custody'] = True
        return vals

    def action_set_custody(self):
        for move in self:
            sale_custody_obj = self.env['sales.custody']
            partner_id = move.picking_id.partner_id.parent_id and move.picking_id.partner_id.parent_id.id or move.picking_id.partner_id.id
            delivery_partner_id = move.picking_id.partner_id.id
            sales_custody = sale_custody_obj.search([('company_id', '=', move.picking_id.company_id.id), ('partner_id', '=', partner_id), ('product_id', '=', move.product_id.id),
                                                     ('delivery_partner_id', '=', delivery_partner_id), ('product_uom', '=', move.product_uom.id)])
            if not sales_custody:
                sales_custody = sale_custody_obj.create({'company_id': move.picking_id.company_id.id, 'partner_id': partner_id, 'product_id': move.product_id.id,
                                                         'delivery_partner_id': delivery_partner_id, 'product_uom': move.product_uom.id})
            sales_custody.move_ids = [(4, move.id)]

            if not sales_custody.price_unit:
                sales_custody.price_unit = move.sale_line_id and move.sale_line_id.price_unit or move.product_id.lst_price
                sales_custody.last_price_from = move.sale_line_id and move.sale_line_id.order_id.name or 'Product Public Price'
            else:
                if move.sale_line_id:
                    sales_custody.price_unit = move.sale_line_id.price_unit
                    sales_custody.last_price_from = move.sale_line_id.order_id.name
