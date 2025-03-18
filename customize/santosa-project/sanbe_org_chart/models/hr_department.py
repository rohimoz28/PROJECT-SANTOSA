from odoo import models, fields, api, tools, _
class HRDepartment(models.Model):
    _inherit = "hr.department"


    branch_id = fields.Many2one('res.branch',string='Branch',index=True)