from odoo import models, fields


class Respartner(models.Model):
    _inherit = "res.partner"

    on_custody = fields.Boolean(string="Sale on custody", track_visibility='onchange', default=False)
