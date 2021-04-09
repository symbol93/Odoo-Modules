# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, tools, _


_logger = logging.getLogger(__name__)


class ReportAccountMoveNir(models.AbstractModel):
    _name = 'report.bart_export_saga.report_account_move_nir'
    _description = 'Aviz Retur'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
        }
