from odoo import fields, models, api


class SbIncompleteAttendanceDetails(models.Model):
    _name = 'sb.incomplete.attendance.details'
    _description = 'Incomplete Attendance Details'

    incomplete_attn_id = fields.Many2one(
        comodel_name='sb.incomplete.attendances',
        string='Incomplete Attendance ID',
        required=False)
    period_id = fields.Many2one('hr.opening.closing', string='Periode', index=True)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    # branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True)
    nik = fields.Char(
        string='NIK',
        required=False)
    name = fields.Char(
        string='Name',
        required=False)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    job_id = fields.Many2one('hr.job', string='Job Position')
    wdcode = fields.Many2one(
        'hr.working.days',
        # domain="[('id','in',wdcode_ids)]",
        string='WD Code',
        copy=True,
        index=True
    )
    empgroup_id = fields.Many2one(
        comodel_name='hr.empgroup',
        string='Emp Group',
        required=False)
    details_date = fields.Date(
        string='Details Date',
        required=False)
    date_timein = fields.Date(
        string='Date TimeIn',
        required=False)
    date_timeout = fields.Date(
        string='Date TimeOut',
        required=False)
    time_in = fields.Float(
        string='Time In',
        required=False)
    time_out = fields.Float(
        string='Time Out',
        required=False)
    status_attendance = fields.Char(
        string='Status Attendance',
        required=False)
    type = fields.Char(
        string='Type',
        required=False)