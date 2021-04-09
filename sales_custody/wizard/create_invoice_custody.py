from odoo import models, fields
from odoo.exceptions import UserError


class InvoiceCustody(models.TransientModel):
    _name = "invoice.custody"

    journal_id = fields.Many2one('account.journal')
    pricelist_id = fields.Many2one('product.pricelist')

    def create_invoice(self):

        sc_obj = self.env['sales.custody']
        lines = sc_obj.browse(self.env.context.get('active_ids', [])).filtered(lambda line: line.qty_to_invoice > 0 and line.qty_available > 0)
        lines_json = sc_obj.search_read([('id', '=', lines.ids)])
        grouped_partners = []
        if lines_json:

            for data in lines_json:
                partner_id = data['partner_id']
                delivery_id = data['delivery_partner_id']
                key = str(partner_id[0]) + "pr," + str(delivery_id[0]) + "p"
                del data['partner_id']

                if key in [res['key'] for res in grouped_partners]:
                    for res in grouped_partners:
                        if res['key'] == key:
                            res['data'].append(data)
                else:
                    grouped_partners.append({'partner_id': partner_id, 'delivery_id': delivery_id, 'key': key, 'data': [data], })
        invoices = self.env['account.move']
        for partner in grouped_partners:
            partner_lines =lines.filtered(lambda line: line.partner_id.id == partner['partner_id'][0] and line.delivery_partner_id.id == partner['delivery_id'][0])
            invoices = invoices | partner_lines._create_invoices(self.journal_id, self.pricelist_id)
        lines.update({'qty_to_invoice': 0})

        return self.action_view_invoice(invoices)

    def action_view_invoice(self, invoices):

        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice'
        }

        action['context'] = context
        return action
