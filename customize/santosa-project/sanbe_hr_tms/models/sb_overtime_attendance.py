from odoo import fields, models, api


class SbOvertimeAttendance(models.Model):
    _name = 'sb.overtime.attendance'
    _description = 'Monitoring OT Request vs Realization'

    no_request = fields.Char(
        string='No Request',
        required=False)
    req_date = fields.Date(
        string='Request Date',
        required=False)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    nik = fields.Char(
        string='NIK',
        required=False)
    req_time_fr = fields.Float(
        string='Req Time Fr',
        required=False)
    req_time_to = fields.Float(
        string='Req Time To',
        required=False)
    rlz_time_fr = fields.Float(
        string='Rel Time Fr',
        required=False)
    rlz_time_to = fields.Float(
        string='Rel Time To',
        required=False)
    approve_time_from = fields.Float(
        string='App Time Fr',
        required=False)
    approve_time_to = fields.Float(
        string='App Time To',
        required=False)
    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
    branch_id = fields.Many2one('res.branch', string='Bisnis Unit', index=True, domain="[('id','in',branch_ids)]")
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department', index=True)
    periode_id = fields.Many2one('hr.opening.closing',string='Period',index=True)
    state = fields.Char(
        string='State',
        required=False)