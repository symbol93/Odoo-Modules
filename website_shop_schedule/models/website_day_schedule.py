from datetime import datetime
import pytz

from odoo import models, fields
from odoo.tools import format_duration


class WebsiteDaySchedule(models.Model):
    _name = "website.day.schedule"
    _order = 'day_of_week'

    day_of_week = fields.Selection([
        ('0', 'Luni'),
        ('1', 'Marti'),
        ('2', 'Miercuri'),
        ('3', 'Joi'),
        ('4', 'Vineri'),
        ('5', 'Sambata'),
        ('6', 'Duminica'),
    ], string='Day of week')
    start_hour = fields.Float(string="Start hour")
    end_hour = fields.Float(string="End hour")
    website_id = fields.Many2one('website', string='Website', required=True, ondelete='cascade', index=True, copy=False)

    def get_label_day_of_week(self):
        return dict(self.fields_get(allfields=['day_of_week'])['day_of_week']['selection'])[self.day_of_week]

    def get_start_hour(self):
        hour = int(self.start_hour)
        return hour

    def get_start_min(self):
        minutes = self.start_hour % 1
        return int(round(minutes * 60, 2))

    def get_end_hour(self):
        hour = int(self.end_hour)
        return hour

    def get_end_min(self):
        minutes = self.end_hour % 1
        return int(round(minutes * 60, 2))


class Website(models.Model):
    _inherit = "website"

    website_day_schedule_ids = fields.One2many('website.day.schedule', 'website_id', string='Day schedule', copy=True, auto_join=True)
    shop_available = fields.Boolean(string="Shop available", default=True)
    close_message = fields.Text(string="Closed shop message")
    is_delivery = fields.Boolean(string="Website for delivery", default=False)

    def get_shop_available(self):
        active = False
        if self.shop_available:
            today = datetime.now(pytz.timezone('Europe/Bucharest'))
            current_day = today.weekday()
            schedule_day = self.website_day_schedule_ids.filtered(lambda day: int(day.day_of_week) == current_day)
            if schedule_day:
                current_hour = today.hour + (today.minute / 60)
                if schedule_day.start_hour < current_hour and schedule_day.end_hour > current_hour:
                    active = True
        return active
