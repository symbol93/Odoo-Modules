# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class IngController(http.Controller):
    _return_url = '/payment/ing/return'
    _cancel_url = '/payment/ing/cancel'

    @http.route([
        '/payment/ing/return/',
    ], type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def ing_return(self, **args):
        _logger.debug('payment_ing_return: %s' % pprint.pformat(args))

        request.env['payment.transaction'].sudo().form_feedback(args, 'ing')
        return werkzeug.utils.redirect('/payment/process')

    @http.route([
        '/payment/ing/cancel/',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def ing_cancel(self, **args):
        _logger.debug('payment_ing_cancel: %s' % pprint.pformat(args))

        tx = self.ing_get_tx(**args)

        if tx.state == 'draft':
            self.ing_validate_data(**args)

        return werkzeug.ing.redirect('/shop/payment')

    def ing_get_tx(self, **args):
        return request.env['payment.transaction'].with_user(SUPERUSER_ID)._ing_form_get_tx_from_data(args)

    def ing_validate_data(self, **args):
        return request.env['payment.transaction'].sudo().form_feedback(args, 'ing')
