from odoo import fields, models, api


class HREmployee(models.Model):
    _inherit = "hr.employee"

    address_ids = fields.One2many('hr.employee.addresses', 'employee_id', auto_join=True, string='Asset Details')
    # states = fields.Selection([
    #     ('draft', "Draft"),
    #     ('req_approval', 'Request For Approval'),
    #     ('rejected', 'Rejected'),
    #     ('approved', 'Approved'),
    #     ('inactive', 'Inactive'),
    #     ('hold', 'Hold'),
    # ], compute='_get_states'
    # )
    
    # def _get_states(self):
    #     for line in self:
    #         return self.env['hr.employee'].browse(line.id).state