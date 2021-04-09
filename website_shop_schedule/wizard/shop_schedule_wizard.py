from odoo import fields, models, api
import datetime


class ShopScheduleWizard(models.TransientModel):
    _name = "shop.schedule.wizard"
    _description = "Shop schedule wizard"

    @api.model
    def default_get(self, fields):
        res = super(ShopScheduleWizard, self).default_get(fields)

        website = self.env['website'].search([('is_delivery', '=', True)], limit=1)
        if not website:
            return res
        if 'website_id' in fields:
            res.update(website_id=website.id)
        if 'shop_available' in fields:
            res.update(shop_available=website.shop_available)
        if 'close_message' in fields:
            res.update(close_message=website.close_message)
        return res

    website_id = fields.Many2one('website')
    website_day_schedule_ids = fields.One2many('website.day.schedule', 'website_id', string='Day schedule', related="website_id.website_day_schedule_ids")
    shop_available = fields.Boolean(string="Shop available")
    close_message = fields.Text(string="Closed shop message")

    def update_data(self):
        self.website_id.sudo().shop_available = self.shop_available
        self.website_id.sudo().close_message = self.close_message
