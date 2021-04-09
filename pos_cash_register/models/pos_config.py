from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    cash_register_ip = fields.Char('Cash Register IP')
    use_cash_register = fields.Boolean('Use Cash Register', default=False)