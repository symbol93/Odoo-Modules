from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    shop_id = fields.Many2one('shop.list', string="Shop")
