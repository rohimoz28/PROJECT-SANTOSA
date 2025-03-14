from odoo import models, fields, api

class Department(models.Model):
    _inherit = "hr.department"

    department_code = fields.Char('Department Code')
    branch_id = fields.Many2one('res.branch',string='Bisnis Unit')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Directorate')
    # @api.depends('department_code','name')
    # def _compute_display_name(self):
    #     for account in self:
    #         account.display_name = f"{account.name}"
            # account.display_name = '%s-%s' % (account.department_code   or '', account.name)