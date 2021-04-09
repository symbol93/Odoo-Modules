from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    shop_id = fields.Many2one('shop.list', string="Shop")
