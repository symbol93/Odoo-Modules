from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    expoerted_saga = fields.Boolean("Exportat Saga", default=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_default_subtotal(self):
        return self.price_subtotal

    subtotal_editable = fields.Float(string="Valoare fara TVA", default=_get_default_subtotal)
    type = fields.Selection(selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ],related="move_id.type")

    @api.onchange('subtotal_editable')
    def onchange_subtotal_editable(self):
        for line in self:
            line.price_unit = line.subtotal_editable / line.quantity

    @api.onchange('price_unit', 'quantity')
    def onchange_priceunit_editable(self):
        for line in self:
            line.subtotal_editable = line.price_unit * line.quantity
