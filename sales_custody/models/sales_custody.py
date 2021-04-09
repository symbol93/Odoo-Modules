from odoo import models, fields, api, _
from odoo.addons.base.models.decimal_precision import dp
from odoo.exceptions import UserError


class SalesCustody(models.Model):
    _name = "sales.custody"

    @api.depends('qty_delivered', 'qty_invoiced')
    def _get_qty_available(self):
        for sales_custody in self:
            sales_custody.qty_available = sales_custody.qty_delivered - sales_custody.qty_invoiced
            sales_custody.amount_available = sales_custody.amount_delivered - sales_custody.amount_invoiced

    @api.depends('invoice_line_ids', 'invoice_line_ids.move_id.state', 'invoice_line_ids.move_id.on_custody')
    def _get_qty_invoiced(self):
        for sales_custody in self:
            qty = sum(line.quantity * (line.move_id.type == 'out_refund' and -1 or 1) for line in sales_custody.invoice_line_ids if line.move_id.state in ['posted'] and line.move_id.on_custody)
            amount = sum(line.price_total for line in sales_custody.invoice_line_ids if line.move_id.state in ['posted'] and line.move_id.on_custody)
            sales_custody.update({'qty_invoiced': qty, 'amount_invoiced': amount})

    @api.depends('move_ids', 'move_ids.picking_id.state', 'move_ids.picking_id.on_custody')
    def _get_qty_delivered(self):
        for sales_custody in self:
            qty = sum(line.quantity_done * (line.picking_id.picking_type_id.code == 'outgoing' and 1 or -1) for line in sales_custody.move_ids if line.picking_id.state in ['done'] and line.picking_id.on_custody)
            amount = sum(
                line.quantity_done * sales_custody.price_unit * (line.picking_id.picking_type_id.code == 'outgoing' and 1 or -1) for line in sales_custody.move_ids if
                line.picking_id.state in ['done'] and line.picking_id.on_custody)
            sales_custody.update({'qty_delivered': qty, 'amount_delivered': amount})

    company_id = fields.Many2one('res.company', string="Company", readonly=1)
    partner_id = fields.Many2one('res.partner', string="Partner", readonly=1)
    delivery_partner_id = fields.Many2one('res.partner', string="Delivery Address", readonly=1)
    product_id = fields.Many2one('product.product', string="Product", readonly=1)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    price_unit = fields.Float(string="Price unit", digits=dp.get_precision('Product Price'), readonly=1)
    qty_delivered = fields.Float(string="Delivered quantity", compute="_get_qty_delivered", store=True, readonly=1)
    qty_invoiced = fields.Float(string="Invoiced quantity", compute="_get_qty_invoiced", store=True, readonly=1)
    qty_available = fields.Float(string="On hand quantity", compute="_get_qty_available", store=True, readonly=1)
    qty_to_invoice = fields.Float(string="Qty", default=0)
    amount_delivered = fields.Float(string="Delivered amount", compute="_get_qty_delivered", store=True, digits=dp.get_precision('Product Price'), readonly=1)
    amount_invoiced = fields.Float(string="Invoiced amount", compute="_get_qty_invoiced", store=True, digits=dp.get_precision('Product Price'), readonly=1)
    amount_available = fields.Float(string="On hand amount", compute="_get_qty_available", store=True, digits=dp.get_precision('Product Price'), readonly=1)
    user_id = fields.Many2one(related="partner_id.user_id", string="Sale Person", store=True, readonly=1)
    move_ids = fields.Many2many('stock.move', 'sales_custody_stock_move_rel', 'sales_custody_id', 'stock_move_id', string="Stock moves", readonly=1)
    invoice_line_ids = fields.Many2many('account.move.line', 'sales_custody_account_move_line_rel', 'sales_custody_id', 'account_move_line_id', string="Invoice lines", readonly=1)
    last_price_from = fields.Char("Last price from")

    _sql_constraints = [
        ('produs_unic', 'unique(company_id, partner_id, product_id, delivery_partner_id, product_uom)', 'You can have only one line of sales custody with those company,partner and product!'),
    ]

    def show_history(self):
        return {
            'name': "History",
            'res_model': 'sales.custody',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('sales_custody.view_sales_custody_form').id,
            'target': 'new',
            'perm_read': 1,
            'flags': {'mode': 'readonly'},
        }

    def _prepare_invoice(self, journal_id):

        invoice_vals = {
            'ref': '',
            'type': 'out_invoice',
            'narration': '',
            'currency_id': self.partner_id.property_product_pricelist.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.delivery_partner_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'invoice_origin': 'Custody Sales',
            'invoice_line_ids': [],
            'on_custody': True,
            'journal_id': journal_id.id
        }
        return invoice_vals

    def _prepare_invoice_line(self, pricelist_id):

        self.ensure_one()
        product = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner=self.partner_id,
            quantity=self.qty_invoiced,
            pricelist=pricelist_id.id,
            uom=self.product_uom.id
        )

        price_unit = pricelist_id.price_get(self.product_id.id, 1)[pricelist_id.id]
        if not price_unit:
            raise UserError(_('There is no price for %s in price list: %s.' % (self.product_id.name, pricelist_id.name)))
        return {
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, self.product_id.taxes_id.ids)],
        }

    def _create_invoices(self, journal_id, pricelist_id):

        # 1) Create invoices.
        invoice_vals_list = []

        # Invoice values.
        invoice_vals = self._prepare_invoice(journal_id)

        # Invoice line values (keep only necessary sections).
        for line in self:
            invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line(pricelist_id)))

        if not invoice_vals['invoice_line_ids']:
            raise UserError(_('There is no invoiceable line.'))

        invoice_vals_list.append(invoice_vals)

        # Create invoices.
        moves = self.env['account.move'].with_context(default_type='out_invoice').create(invoice_vals_list)

        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                                        values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                                        subtype_id=self.env.ref('mail.mt_note').id
                                        )
        return moves

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = {
            'product_id': return_line.product_id.id,
            'name': return_line.product_id.name,
            'product_uom_qty': return_line.qty_to_invoice,
            'product_uom': return_line.product_uom.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': new_picking.location_dest_id.id,
            'location_dest_id': new_picking.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': new_picking.picking_type_id.warehouse_id.id,
            'procure_method': 'make_to_stock',
            'partner_id': self.delivery_partner_id.id,
        }
        return vals

    def _create_pickings(self, warehouse_id):
        # create new picking for returned products
        picking_type_id = warehouse_id.in_type_id
        location_id = picking_type_id.default_location_dest_id
        dest_location_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
        new_picking = self.env['stock.picking'].create({
            'partner_id': self.delivery_partner_id.id,
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': _("Return from custody sales "),
            'location_id': location_id.id,
            'location_dest_id': dest_location_id.id,
            'on_custody': True
        })
        new_picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': new_picking, 'origin': self},
                                           subtype_id=self.env.ref('mail.mt_note').id)

        for line in self:
            vals = self._prepare_move_default_values(line, new_picking)
            self.env['stock.move'].create(vals)

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking
