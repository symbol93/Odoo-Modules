from odoo import models


class AccountMoveExportSaga(models.TransientModel):
    _name = "account.move.export.saga.wizard"
    _description = "Export saga"

    def export_saga(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/xml/export_saga?ids=%s' % self.env.context.get('active_ids', []),
            'target': 'self',
        }
