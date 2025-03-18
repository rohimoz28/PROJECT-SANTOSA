from odoo import fields, models, api


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'
    _description = 'inherit from hr_attendance'

    empgroup_id = fields.Many2one(
        comodel_name='hr.empgroup',
        string='Emp. Group',
        required=False)