from odoo import fields, models, api

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    manager_id = fields.Many2one('parent.hr.employee', related='employee_id.parent_id', tracking=True, string="Manager")