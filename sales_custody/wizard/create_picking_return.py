from odoo import models, fields
from odoo.exceptions import UserError


class PickingReturnCustody(models.TransientModel):
    _name = "picking.return.custody"

    warehouse_id = fields.Many2one('stock.warehouse')

    def create_return(self):

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
        pickings = self.env['stock.picking']
        for partner in grouped_partners:
            partner_lines = lines.filtered(lambda line: line.partner_id.id == partner['partner_id'][0] and line.delivery_partner_id.id == partner['delivery_id'][0])
            pickings = pickings | partner_lines._create_pickings(self.warehouse_id)
        lines.update({'qty_to_invoice': 0})

        return self.action_view_pickings(pickings)

    def action_view_pickings(self, pickings):

        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id

        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_picking_id=picking_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_group_id=picking_id.group_id.id)
        return action
