from odoo import models, fields, api


class ShopList(models.Model):
    _name = "shop.list"
    _description = "Shop"

    name = fields.Char(string="Name")
    product_ids = fields.Many2many(
        'product.product',
        'shop_product_rel',
        'shop_id',
        'product_id',
        string='Products',
        )
    website_categ_ids = fields.Many2one('product.public.category', compute="get_website_categs")

    @api.depends('product_ids')
    def get_website_categs(self):
        for line in self:
            line.website_categ_ids = [(6, 0, line.product_ids.public_categ_ids.ids)]
