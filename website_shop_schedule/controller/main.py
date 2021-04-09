from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo import http
from odoo.http import request


class WebsiteSale(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        rez = super(WebsiteSale, self)._prepare_product_values(product, category, search, **kwargs)
        rez['shop_available'] = request.website.get_shop_available()
        rez['close_message'] = request.website.close_message
        return rez

    def _get_shop_payment_values(self, order, **kwargs):
        rez = super(WebsiteSale, self)._get_shop_payment_values(order, **kwargs)
        rez['shop_available'] = request.website.get_shop_available()
        rez['close_message'] = request.website.close_message
        return rez


class MainController(http.Controller):
    @http.route('/shopschedule', type='http', auth='public', website=True)
    def web_address_required(self, *args, **kw):
        qcontext = request.params.copy()
        qcontext['schedule_lines'] = request.website.website_day_schedule_ids
        response = request.render('website_shop_schedule.shop_schedule', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
