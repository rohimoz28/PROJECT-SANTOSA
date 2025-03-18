from odoo import fields, models


class SbOvertimeBundling(models.Model):
    _name = "sb.overtime.bundling"
    _description = "Overtime Bundling"

    branch_id = fields.Many2one('res.branch', string='Bisnis Unit', index=True, domain="[('id','in',branch_ids)]")
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department', index=True)
    no_request = fields.Char(string='No Request')
    req_date = fields.Date(string='Request Date')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    nik = fields.Char(string='NIK')
    req_time_fr = fields.Float(string='Req Time From')
    req_time_to = fields.Float(string='Req Time To')
    approve_time_from = fields.Float(string='App Time From')
    approve_time_to = fields.Float(string='App Time To')
    rlz_time_fr = fields.Float(string='Rel Time From')
    rlz_time_to = fields.Float(string='Rel Time To')
    sequence = fields.Integer(string='Sequence')
    realtime_bundling_from = fields.Float(string='Realtime Bundling From')
    realtime_bundling_to = fields.Float(string='Realtime Bundling To')
    state = fields.Char(string='State')
    periode_id = fields.Many2one('hr.opening.closing',string='Period',index=True)
    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
