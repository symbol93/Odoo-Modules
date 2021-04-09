from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sync_child = fields.Boolean(string="Syncronize Accounts Child Categories", default=True)

    def write(self, vals):
        rez = super(ProductCategory, self).write(vals)
        for line in self:
            if line.sync_child and line.child_id:
                if 'property_account_income_categ_id' in vals:
                    line.child_id.update({'property_account_income_categ_id': vals['property_account_income_categ_id']})
                if 'property_account_expense_categ_id' in vals:
                    line.child_id.update({'property_account_expense_categ_id': vals['property_account_expense_categ_id']})
                if 'property_stock_account_input_categ_id' in vals:
                    line.child_id.update({'property_stock_account_input_categ_id': vals['property_stock_account_input_categ_id']})
                if 'property_stock_account_output_categ_id' in vals:
                    line.child_id.update({'property_stock_account_output_categ_id': vals['property_stock_account_output_categ_id']})
                if 'property_stock_valuation_account_id' in vals:
                    line.child_id.update({'property_stock_valuation_account_id': vals['property_stock_valuation_account_id']})
            if 'parent_id' in vals:
                parent = self.env['product.category'].browse(vals['parent_id'])
                line.property_account_income_categ_id = parent.property_account_income_categ_id
                line.property_account_expense_categ_id = parent.property_account_expense_categ_id
                line.property_stock_account_input_categ_id = parent.property_stock_account_input_categ_id
                line.property_stock_account_output_categ_id = parent.property_stock_account_output_categ_id
                line.property_stock_valuation_account_id = parent.property_stock_valuation_account_id
        return rez

