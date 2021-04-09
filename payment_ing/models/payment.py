# -*- coding: utf-8 -*-
import json
import pprint
import pytz
import time
import requests
import datetime as DT
from werkzeug import urls
from addons.payment.models.payment_acquirer import _partner_format_address, _partner_split_name
from odoo.tools import float_compare, float_repr, float_round, datetime, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

import logging

_logger = logging.getLogger(__name__)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'  # 2018-04-20T15:47:52+0300
TIMEZONE_CUR = pytz.timezone(time.tzname[0])
TIMEZONE_UTC = pytz.timezone('UTC')

ALLOWED_TIMEDELTA = DT.timedelta(minutes=5)

TEST_REGISTER_ENDPOINT = "https://securepay-uat.ing.ro/mpi_uat/rest/register.do"
PRODUCTION_REGISTER_ENDPOINT = "https://securepay.ing.ro/mpi/rest/register.do"

TEST_VERIFY_ENDPOINT = "https://securepay-uat.ing.ro/mpi_uat/rest/getOrderStatusExtended.do"
PRODUCTION_VERIFY_ENDPOINT = "https://securepay.ing.ro/mpi/rest/getOrderStatus.do"


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('ing', 'Ing'), ], )

    ing_user = fields.Text('User')
    ing_password = fields.Char('Parola')

    def get_form_action_url_ing(self, values):
        """ Returns the form action URL, for form-based acquirer implementations. """
        if hasattr(self, '%s_get_form_action_url' % self.provider):
            return getattr(self, '%s_get_form_action_url' % self.provider)(values)
        return False

    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        """ Renders the form template of the given acquirer as a qWeb template.
        :param string reference: the transaction reference
        :param float amount: the amount the buyer has to pay
        :param currency_id: currency id
        :param dict partner_id: optional partner_id to fill values
        :param dict values: a dictionary of values for the transction that is
        given to the acquirer-specific method generating the form values

        All templates will receive:

         - acquirer: the payment.acquirer browse record
         - user: the current user browse record
         - currency_id: id of the transaction currency
         - amount: amount of the transaction
         - reference: reference of the transaction
         - partner_*: partner-related values
         - partner: optional partner browse record
         - 'feedback_url': feedback URL, controler that manage answer of the acquirer (without base url) -> FIXME
         - 'return_url': URL for coming back after payment validation (wihout base url) -> FIXME
         - 'cancel_url': URL if the client cancels the payment -> FIXME
         - 'error_url': URL if there is an issue with the payment -> FIXME
         - context: Odoo context

        """
        if values is None:
            values = {}

        if not self.view_template_id:
            return None

        values.setdefault('return_url', '/payment/process')
        # reference and amount
        values.setdefault('reference', reference)
        amount = float_round(amount, 2)
        values.setdefault('amount', amount)

        # currency id
        currency_id = values.setdefault('currency_id', currency_id)
        if currency_id:
            currency = self.env['res.currency'].browse(currency_id)
        else:
            currency = self.env.company.currency_id
        values['currency'] = currency

        # Fill partner_* using values['partner_id'] or partner_id argument
        partner_id = values.get('partner_id', partner_id)
        billing_partner_id = values.get('billing_partner_id', partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner_id != billing_partner_id:
                billing_partner = self.env['res.partner'].browse(billing_partner_id)
            else:
                billing_partner = partner
            values.update({
                'partner': partner,
                'partner_id': partner_id,
                'partner_name': partner.name,
                'partner_lang': partner.lang,
                'partner_email': partner.email,
                'partner_zip': partner.zip,
                'partner_city': partner.city,
                'partner_address': _partner_format_address(partner.street, partner.street2),
                'partner_country_id': partner.country_id.id,
                'partner_country': partner.country_id,
                'partner_phone': partner.phone,
                'partner_state': partner.state_id,
                'billing_partner': billing_partner,
                'billing_partner_id': billing_partner_id,
                'billing_partner_name': billing_partner.name,
                'billing_partner_commercial_company_name': billing_partner.commercial_company_name,
                'billing_partner_lang': billing_partner.lang,
                'billing_partner_email': billing_partner.email,
                'billing_partner_zip': billing_partner.zip,
                'billing_partner_city': billing_partner.city,
                'billing_partner_address': _partner_format_address(billing_partner.street, billing_partner.street2),
                'billing_partner_country_id': billing_partner.country_id.id,
                'billing_partner_country': billing_partner.country_id,
                'billing_partner_phone': billing_partner.phone,
                'billing_partner_state': billing_partner.state_id,
            })
        if values.get('partner_name'):
            values.update({
                'partner_first_name': _partner_split_name(values.get('partner_name'))[0],
                'partner_last_name': _partner_split_name(values.get('partner_name'))[1],
            })
        if values.get('billing_partner_name'):
            values.update({
                'billing_partner_first_name': _partner_split_name(values.get('billing_partner_name'))[0],
                'billing_partner_last_name': _partner_split_name(values.get('billing_partner_name'))[1],
            })

        # Fix address, country fields
        if not values.get('partner_address'):
            values['address'] = _partner_format_address(values.get('partner_street', ''),
                                                        values.get('partner_street2', ''))
        if not values.get('partner_country') and values.get('partner_country_id'):
            values['country'] = self.env['res.country'].browse(values.get('partner_country_id'))
        if not values.get('billing_partner_address'):
            values['billing_address'] = _partner_format_address(values.get('billing_partner_street', ''),
                                                                values.get('billing_partner_street2', ''))
        if not values.get('billing_partner_country') and values.get('billing_partner_country_id'):
            values['billing_country'] = self.env['res.country'].browse(values.get('billing_partner_country_id'))

        # compute fees
        fees_method_name = '%s_compute_fees' % self.provider
        if hasattr(self, fees_method_name):
            fees = getattr(self, fees_method_name)(values['amount'], values['currency_id'],
                                                   values.get('partner_country_id'))
            values['fees'] = float_round(fees, 2)

        # call <name>_form_generate_values to update the tx dict with acqurier specific values
        cust_method_name = '%s_form_generate_values' % (self.provider)
        if hasattr(self, cust_method_name):
            method = getattr(self, cust_method_name)
            values = method(values)
        if self.provider == 'ing':
            url = self._context.get('tx_url', self.get_form_action_url_ing(values))
        else:
            url = self._context.get('tx_url', self.get_form_action_url())
        values.update({
            'tx_url': url,
            'submit_class': self._context.get('submit_class', 'btn btn-link'),
            'submit_txt': self._context.get('submit_txt'),
            'acquirer': self,
            'user': self.env.user,
            'context': self._context,
            'type': values.get('type') or 'form',
        })

        _logger.info('payment.acquirer.render: <%s> values rendered for form payment:\n%s', self.provider,
                     pprint.pformat(values))
        return self.view_template_id.render(values, engine='ir.qweb')

    def ing_get_form_action_url(self, values):
        base_url = self.get_base_url()
        params = {'userName': self.ing_user,
                  'password': self.ing_password,
                  'currency': '946',
                  'description': 'Comanda laceaun.ro nr %s' % values['reference'],
                  'amount': ("%.2f" % values['amount']).replace('.', ''),
                  'returnUrl': urls.url_join(base_url, 'payment/ing/return?id=%s' % (values['reference'])),
                  'language': '',
                  'email': values['partner_email'],
                  'reconciliationId': '',
                  'orderBundle': {},
                  'jsonParams': json.dumps({'FORCE_3DS2': 'true'}),
                  }

        url = PRODUCTION_REGISTER_ENDPOINT
        if self.state == "test":
            url = TEST_REGISTER_ENDPOINT
        r = requests.post(url, data=params)
        data = r.text
        if data:
            obj = json.loads(r.content.decode("UTF-8"))
            values.update({'mdOrder': obj['orderId']})
            return obj['formUrl']
        return

    def ing_form_generate_values(self, values):
        """
        method that generates the values used to render the form button template.
        """
        _logger.debug('_ing_form_generate_values before: %s, %s' % (self.ids, pprint.pformat(values)))
        self.ensure_one()
        return values


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    ing_paid = fields.Selection([('0', 'Neplatit'), ('1', 'Platit'), ('2', 'Anulat')], string="Status ing",
                                help='0-neplatit,1-platit,2-anulat')
    ing_orderid = fields.Char("Ing Order Id")
    ing_message = fields.Char("Mesaj")

    @api.model
    def _ing_form_get_tx_from_data(self, data={}):
        _logger.debug('_ing_form_get_tx_from_data: %s' % pprint.pformat(data))

        reference = data.get('id')
        if not reference:
            error_msg = 'Ing: received data with missing reference: %s' % pprint.pformat(data)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx_ids = self.search([('reference', '=', reference)])

        if len(tx_ids) != 1:
            error_msg = 'Ing: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no transaction found'
            else:
                error_msg += '; multiple transactions found: %s' % tx_ids.ids
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx_ids[0]

    def _ing_form_get_invalid_parameters(self, data):
        _logger.debug('_ing_form_get_invalid_parameters: %s, %s' % (self.ids, pprint.pformat(data)))
        self.ensure_one()
        invalid_parameters = []

        return invalid_parameters

    def _set_transaction_pending(self):
        # Override of '_set_transaction_pending' in the 'payment' module
        # to sent the quotations automatically.
        super(PaymentTransaction, self)._set_transaction_pending()

        for record in self:
            sales_orders = record.sale_order_ids.filtered(lambda so: so.state in ['draft', 'sent'])
            sales_orders.filtered(lambda so: so.state == 'draft').with_context(tracking_disable=True).write(
                {'state': 'sent'})

            if record.acquirer_id.provider == 'transfer':
                for so in record.sale_order_ids:
                    so.reference = record._compute_sale_order_reference(so)

    def _ing_form_validate(self, data):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info('ING: trying to validate an already validated tx (ref %s)', self.reference)
            return True

        params = {'orderId': data.get('orderId'),
                  'userName': self.acquirer_id.ing_user,
                  'password': self.acquirer_id.ing_password,
                  'language': '',
                  }
        url = PRODUCTION_VERIFY_ENDPOINT
        if self.acquirer_id.state == "test":
            url = TEST_VERIFY_ENDPOINT
        r = requests.post(url, data=params)
        response = r.text
        error = ""
        if response:
            obj_res = json.loads(response)
            if obj_res['ErrorCode'] == '0' and obj_res['OrderStatus'] == 2:
                status = "succeeded"
            else:
                status = "cancelled"
                error = "Eroare la procesarea platii: " + obj_res['ErrorMessage']
        else:
            status = "processing"

        vals = {
            "date": fields.datetime.now(),
            "acquirer_reference": data.get('orderId'),
            "ing_orderid": data.get('orderId'),
        }
        if status == 'succeeded':
            vals.update({'ing_paid': '1'})
            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            return True
        elif status in ('processing', 'requires_action'):
            vals.update({'ing_paid': '0'})
            self.write(vals)
            self.sudo()._set_transaction_pending()
            return True
        else:
            vals.update({'ing_paid': '2'})
            vals.update({'ing_message': error})
            vals.update({'state_message': error})
            self.write(vals)
            self._set_transaction_error(error)
            return True

    def _set_transaction_cancel_ing(self):
        # Cancel the existing payments.
        self.mapped('payment_id').cancel()

        self.write({'state': 'cancel', 'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        self._log_payment_transaction_received()

    def check_ing_status(self):
        filters = [('ing_paid', '=', '0'), ('acquirer_id.ing_user', '!=', False), ('ing_orderid', '!=', False)]
        transactions = self.search(filters)
        for transaction in transactions:
            params = {'orderId': transaction.ing_orderid,
                      'userName': transaction.acquirer_id.ing_user,
                      'password': transaction.acquirer_id.ing_password,
                      'language': '',
                      }
            url = PRODUCTION_VERIFY_ENDPOINT
            if transaction.acquirer_id.state == "test":
                url = TEST_VERIFY_ENDPOINT
            r = requests.post(url, data=params)
            response = r.text
            vals = {}
            if response:
                obj_res = json.loads(response)
                if obj_res['errorCode'] == '0' and obj_res['orderStatus'] == 2:
                    vals.update({'ing_paid': '1'})
                    transaction.write(vals)
                    transaction._set_transaction_done()
                    transaction.execute_callback()
                else:
                    transaction.paid_ing = '2'
                    vals.update({'ing_paid': '2'})

                    transaction.write(vals)
                    transaction._set_transaction_cancel_ing()
            else:
                transaction.paid_ing = '2'

                vals.update({'ing_paid': '2'})

                transaction.write(vals)
                transaction._set_transaction_cancel_ing()
