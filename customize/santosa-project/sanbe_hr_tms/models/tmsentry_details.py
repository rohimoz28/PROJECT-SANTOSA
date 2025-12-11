from odoo import fields, models, api
from odoo.exceptions import UserError

TMS_STATUS_ATTENDEE = [
    ('attendee', 'Draft'),
    ('approved', 'Approved')
]


class TmsentryDetails(models.Model):
    _name = 'sb.tms.tmsentry.details'
    _description = 'Details of hr_tmsentry_summary'

    tmsentry_id = fields.Many2one(
        comodel_name='hr.tmsentry.summary',
        string='TMS Entry'
    )
    details_date = fields.Date(
        string='Date',
        required=False)
    type = fields.Char(string='Day Type')
    workingday_id = fields.Many2one(
        comodel_name='hr.working.days',
        string='WD'
    )
    date_in = fields.Date(string='Date In')
    flag = fields.Char()
    time_in = fields.Float(string='Actual Time In')
    date_out = fields.Date(string='Date Out')
    time_out = fields.Float(string='Actual Time Out')
    status_attendee = fields.Selection(
        string='Status Attendee',
        selection=[('attendee', 'Attendee'),
                   ('absent', 'Absent'), ],
        required=False
    )
    status_attendance = fields.Char(
        string='Status Attendance',
        required=False)
    delay = fields.Integer(string='Delay')
    positive_delay = fields.Integer(compute='_compute_positive_delay', store=False)
    status = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('reject', 'Reject'),
            ('done', 'Close'), ],
        required=False, default='draft',
        compute='_compute_approved',
        store=True
    )
    empgroup_id = fields.Many2one(
        comodel_name='hr.empgroup',
        string='Employee Group',
        required=False
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee ID',
        required=False
    )
    emp_id = fields.Char(
        'Employee ID', 
        related='employee_id.employee_id'
    )
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    
    plann_date_from = fields.Date(string='Approval Date From')
    plann_date_to = fields.Date(string='Approval Date To')
    approval_ot_from = fields.Float(string='Appv OT Fr')
    approval_ot_to = fields.Float(string='Appv OT To')
    aot1 = fields.Float(string='AOT1')
    aot2 = fields.Float(string='AOT2')
    aot3 = fields.Float(string='AOT3')
    aot4 = fields.Float(string='AOT4')
    ot_type = fields.Selection([('regular', 'Regular'),
                                ('holiday', 'Holiday'),
                                ('dp', 'DP')], string='Tipe SPL')
    oto = fields.Integer(string='OTO')
    premi_attendee = fields.Float('Premi Attendee')
    transport = fields.Float('Transport')
    meal = fields.Float('Meal')
    night_shift = fields.Float('Night Shift 1')
    night_shift2 = fields.Float('Night Shift 2')
    approved = fields.Boolean('Checked by HRD', tracking=True)
    approved_by_ca = fields.Boolean('Approved by CA', tracking=True)
    dayname = fields.Char(string='Day', required=False)
    schedule_time_in = fields.Float(string='Schedule Time In')
    schedule_time_out = fields.Float(string='Schedule Time Out')
    edited_time_in = fields.Float(string='Edited Time In')
    edited_time_out = fields.Float(string='Edited Time Out')
    remark_edit_attn = fields.Text(
        string="Remark Edit Attn",
        help="Remark for edit actual time in & time out",
        required=False)
    is_edited = fields.Boolean(
        string='Edited',
        required=False,
        compute='_compute_is_edited',
        help='Checked if Time In or Time Out Has Been Edited',
        store=True
    )
    delay_allow = fields.Integer(
        string='Allowed Delay',
        required=False)
    delay_level1 = fields.Integer(
        string='Delay1',
        help='delay more than five minutes but under ten minutes',
        required=False)
    delay_level2 = fields.Integer(
        string='Delay1',
        help='delay more than ten minutes',
        required=False)

    @api.depends('edited_time_in', 'edited_time_out', 'date_in', 'date_out')
    def _compute_is_edited(self):
        for record in self:
            record.is_edited = bool(
                record.edited_time_in or record.edited_time_out or record.date_in or record.date_out)

    @api.depends('delay')
    def _compute_positive_delay(self):
        for record in self:
            record.positive_delay = max(record.delay, 0)

    @api.depends('approved')
    def _compute_approved(self):
        for record in self:
            if record.tmsentry_id.state == 'closed':
                raise UserError("The document is closed. Attendance can not be modify.")

            if record.approved:
                record.status = 'approved'
            else:
                record.status = 'draft'

    # def action_view_tms_details(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'sb.tms.tmsentry.details',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'res_id': self.id,
    #         'context': False,
    #     }

    def action_view_tms_details(self):
        return {
            'name': 'action_view_tms_details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sb.tms.tmsentry.details',
            # 'views': [(False, 'form')],
            # 'view_id': False,
            'view_id': self.env.ref('sanbe_hr_tms.tmsentry_details_form_view').id,
            'target': 'new',
            'res_id': self.id,
            'context': False,
        }
