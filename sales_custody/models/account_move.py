from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    on_custody = fields.Boolean(string="Sale on custody", track_visibility='onchange', default=False, states={'open': [('readonly', False)]})

    @api.model
    def create(self, vals):
        rez = super(AccountMove, self).create(vals)
        order = rez.invoice_line_ids.mapped('sale_line_ids') and rez.invoice_line_ids.mapped('sale_line_ids')[0].order_id
        if order:
            rez.update({'on_custody': order.on_custody})
        return rez

    def action_post(self):
        rez = super(AccountMove, self).action_post()
        for move in self:
            if move.on_custody:
                move.mapped('line_ids').action_set_custody()
        return rez


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def action_set_custody(self):
        for line in self.filtered(lambda line: line.product_id):
            sale_custody_obj = self.env['sales.custody']
            partner_id = line.move_id.partner_id.parent_id and line.move_id.partner_id.parent_id.id or line.move_id.partner_id.id,
            sales_custody = sale_custody_obj.search([('company_id', '=', line.move_id.company_id.id), ('partner_id', '=', partner_id), ('product_id', '=', line.product_id.id),
                                                     ('delivery_partner_id', '=', line.move_id.partner_shipping_id.id), ('product_uom', '=', line.product_uom_id.id)])
            if not sales_custody:
                sales_custody = sale_custody_obj.create({'company_id': line.move_id.company_id.id, 'partner_id': partner_id, 'product_id': line.product_id.id,
                                                         'delivery_partner_id': line.move_id.partner_shipping_id.id, 'product_uom': line.product_uom_id.id})
            sales_custody.invoice_line_ids = [(4, line.id)]
