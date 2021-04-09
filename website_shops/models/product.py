from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    shop_ids = fields.Many2many('shop.list', 'shop_product_rel', 'product_id', 'shop_id', string='Shops', )
