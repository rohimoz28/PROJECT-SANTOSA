from odoo import fields, models, api


TMS_ENTRY_STATE = [
    ('draft', 'Draft'),
    ('running', 'Running'),
    ('approved', "Approved"),
    ('done', "Close"),
    ('transfer_payroll', 'Transfer Payroll'),
]


class SBAttndanceCorrectionDetails(models.Model):
    _name = 'sb.attendance.correction.details'
    _description = 'Attendance Correction Details'

    attn_correction_id = fields.Many2one(
        comodel_name='sb.attendance.corrections',
        string='Attendance Correction',
        required=False)
    period_id = fields.Many2one('hr.opening.closing', string='Periode', index=True)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True)
    nik = fields.Char(
        string='NIK',
        required=False)
    name = fields.Char(
        string='Name',
        required=False)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    division_id = fields.Many2one('sanhrms.division', string='Divisi', store=True, readonly="state =='done'")
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen', store=True, readonly="state =='done'")
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', store=True , readonly="state =='done'")
    job_id = fields.Many2one('hr.job', string='Job Position')
    wdcode = fields.Many2one(
        'hr.working.days',
        string='WD Code',
        copy=True,
        index=True
    )
    tgl_time_in = fields.Date(
        string='Tgl Time in',
        required=False)
    time_in = fields.Float(
        string='Time in',
        required=False)
    edited_time_in = fields.Float(
        string='Edited Time in',
        required=False)
    tgl_time_out = fields.Date(
        string='Tgl Time out',
        required=False)
    time_out = fields.Float(
        string='Time out',
        required=False)
    edited_time_out = fields.Float(
        string='Edited Time out',
        required=False)
    delay = fields.Float(
        string='Delay',
        required=False)
    remark = fields.Char(string='Remark', required=False)
    empgroup_id = fields.Many2one(
        comodel_name='hr.empgroup', string='Emp Group', required=False)
    state = fields.Selection(
        selection=TMS_ENTRY_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        store=True,
        default='draft')


class SBLossAttndancenDetails(models.Model):
    _name = 'sb.loss.attendance.details'
    _description = 'Attendance Correction Details'

    attn_correction_id = fields.Many2one(
        comodel_name='sb.attendance.corrections',
        string='Attendance Correction',
        required=False)
    period_id = fields.Many2one(
        'hr.opening.closing', string='Periode', related='attn_correction_id.period_id', store=True, index=True)
    area_id = fields.Many2one(
        'res.territory', related="employee_id.area", string='Area', index=True)
    branch_id = fields.Many2one(
        'res.branch', string='Business Unit', related="employee_id.branch_id", index=True)
    nik = fields.Char(
        string='NIK',
        related='employee_id.nik',
        store=True,
        required=False)
    name = fields.Char(
        string='Name',
        related='employee_id.name',
        store=True,
        required=False)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', store=True, readonly="state =='done'")
    department_id = fields.Many2one(
        'hr.department', related="employee_id.department_id", string='Sub Department')
    division_id = fields.Many2one(
        'sanhrms.division', string='Divisi', store=True, related="employee_id.division_id", readonly="state =='done'")
    hrms_department_id = fields.Many2one(
        'sanhrms.department', string='Departemen', store=True, related="employee_id.hrms_department_id", readonly="state =='done'")
    directorate_id = fields.Many2one(
        'sanhrms.directorate', string='Direktorat', store=True, related="employee_id.directorate_id", readonly="state =='done'")
    job_id = fields.Many2one(
        'hr.job', related="employee_id.job_id", string='Job Position', store=True)
    wdcode = fields.Many2one(
        'hr.working.days',
        string='WD Code',
        related="employee_id.workingdays_id",
        copy=True,
        index=True
    )
    # empgroup_id = fields.Many2one(
    #     comodel_name='hr.empgroup', string='Emp Group', required=False)

    # tgl_time_in = fields.Date(
    #     string='Tgl Time in',
    #     required=False)
    # tgl_time_out = fields.Date(
    #     string='Tgl Time out',
    #     required=False)

    # edited_time_in = fields.Float(
    #     string='Edited Time in',
    #     required=False)
    # edited_time_out = fields.Float(
    #     string='Edited Time Out',
    #     required=False)
    details_date = fields.Date(
        string='Tanggal',
        required=False)
    schedule_time_in = fields.Float(
        string='Schedule Time in',
        required=False)
    schedule_time_out = fields.Float(
        string='Schedule Time out',
        required=False)
    time_in = fields.Float(
        string='Time in',
        required=False)
    time_out = fields.Float(
        string='Time out',
        required=False)
    positive_delay = fields.Float(
        string='Positive Delay',
        required=False)
    remark = fields.Char(string='Remark', required=False)
    state = fields.Selection(
        selection=TMS_ENTRY_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        store=True,
        default='draft')
    attendance_status = fields.Char(store=True, string='Attendance Status')
