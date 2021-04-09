from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    on_custody = fields.Boolean(string="Sale on custody", track_visibility='onchange', default=False, states={'open': [('readonly', False)]})

    @api.onchange('partner_id')
    def onchange_partnerid(self):
        self.on_custody = False
        partner = self.partner_id
        if self.partner_id.parent_id:
            partner = self.partner_id.parent_id
        if partner.on_custody:
            self.on_custody = True

