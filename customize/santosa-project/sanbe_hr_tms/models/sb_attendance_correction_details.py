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
    period_id = fields.Many2one(
        'hr.opening.closing', string='Periode', store=True, index=True)
    area_id = fields.Many2one(
        'res.territory', string='Area', index=True)
    branch_id = fields.Many2one(
        'res.branch', string='Business Unit', index=True)
    nik = fields.Char(
        string='NIK',
        store=True,
        required=False)
    name = fields.Char(
        string='Name',
        store=True,
        required=False)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', store=True, readonly="state =='done'")
    department_id = fields.Many2one(
        'hr.department', string='Sub Department')
    division_id = fields.Many2one(
        'sanhrms.division', string='Divisi', store=True, readonly="state =='done'")
    hrms_department_id = fields.Many2one(
        'sanhrms.department', string='Departemen', store=True,
        readonly="state =='done'")
    directorate_id = fields.Many2one(
        'sanhrms.directorate', string='Direktorat', store=True,
        readonly="state =='done'")
    job_id = fields.Many2one(
        'hr.job', string='Job Position')
    workingday_id = fields.Integer(
        string='Workingday_id',
        required=False)
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
        required=False,
        ondelete='cascade')

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=False,
        ondelete='restrict')

    period_id = fields.Many2one(
        comodel_name='hr.opening.closing',
        string='Period',
        required=False,
        ondelete='restrict')

    area_id = fields.Many2one(
        comodel_name='res.territory',
        string='Area',
        required=False,
        ondelete='restrict')

    branch_id = fields.Many2one(
        comodel_name='res.branch',
        string='Business Unit',
        required=False,
        ondelete='restrict')

    division_id = fields.Many2one(
        comodel_name='sanhrms.division',
        string='Division',
        required=False,
        ondelete='restrict')

    hrms_department_id = fields.Many2one(
        comodel_name='sanhrms.department',
        string='Department',
        required=False,
        ondelete='restrict')

    directorate_id = fields.Many2one(
        comodel_name='sanhrms.directorate',
        string='Directorate',
        required=False,
        ondelete='restrict')

    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Job Position',
        required=False,
        ondelete='restrict')

    workingday_id = fields.Many2one(
        comodel_name='hr.working.days',
        string='Working Days Code',
        required=False,
        ondelete='restrict')

    wdcode = fields.Many2one(
        comodel_name='hr.working.days',
        string='WD Code',
        required=False,
        ondelete='restrict')

    # ===== DATA FIELDS =====
    nik = fields.Char(
        string='NIK',
        required=False)

    name = fields.Char(
        string='Employee Name',
        required=False)

    details_date = fields.Date(
        string='Date',
        required=False)

    schedule_time_in = fields.Float(
        string='Schedule Time In',
        required=False)

    schedule_time_out = fields.Float(
        string='Schedule Time Out',
        required=False)

    time_in = fields.Float(
        string='Time In',
        required=False)

    time_out = fields.Float(
        string='Time Out',
        required=False)

    positive_delay = fields.Float(
        string='Positive Delay',
        required=False)

    delay_minutes = fields.Float(
        string='Delay (minutes)',
        required=False)

    attendance_status = fields.Char(
        string='Attendance Status',
        required=False)

    remark = fields.Char(
        string='Remark',
        required=False)

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        store=True,
        default='draft')
