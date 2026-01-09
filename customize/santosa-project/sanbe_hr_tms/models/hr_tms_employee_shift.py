from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import pytz
from datetime import datetime, time, timedelta, date

TMS_ENTRY_STATE = [
    ('draft', 'Draft'),
    ('review', 'Review HRD'),
    ('approved', 'Disetujui HRD'),
    ('reject', 'Reject'),
]


class HrTMSEmployeeShift(models.Model):
    _name = "sb.employee.shift"
    _description = 'Employee Shift Management'
    # _order = "periode_id desc, directorate_id asc, hrms_department_id asc, division_id asc, jabatan asc"
    # _order = "periode_id desc"

    def _get_running_periode(self):
        """Mendapatkan periode 'running' yang aktif untuk Branch pengguna saat ini."""
        user_branch_id = self.env.user.branch_id.id
        if not user_branch_id:
            return False

        return self.env['hr.opening.closing'].search([
            ('state_process', '=', 'running'),
            ('branch_id', '=', user_branch_id),
            ('open_periode_from', '<=', fields.Datetime.now()),
            ('open_periode_to', '>=', fields.Datetime.now())
        ], order='id desc', limit=1)

    periode_id = fields.Many2one(
        'hr.opening.closing',
        string='Period',
        index=True,
        default=_get_running_periode,
        domain="[('state_process','in',('draft','running'))]"
    )

    period_text = fields.Char(
        string='Period Text', compute='_compute_period_text', store=True, index=True)

    @api.depends('periode_id.open_periode_from', 'periode_id.open_periode_to', 'periode_id.name', 'periode_id.branch_id')
    def _compute_period_text(self):
        """Menghitung teks periode."""
        for rec in self:
            if rec.periode_id:
                periode = rec.periode_id
                date_from = fields.Date.to_string(
                    periode.open_periode_from) if periode.open_periode_from else ''
                date_to = fields.Date.to_string(
                    periode.open_periode_to) if periode.open_periode_to else ''

                formatted_from = fields.Datetime.from_string(
                    date_from).strftime('%d/%m') if date_from else ''
                formatted_to = fields.Datetime.from_string(
                    date_to).strftime('%d/%m') if date_to else ''
                month_str = fields.Datetime.from_string(
                    date_to).strftime("%B %Y") if date_to else ''
                period_name = periode.branch_id.branch_code or ''
                rec.period_text = f"{formatted_from} - {formatted_to} | {month_str} {period_name}"
            else:
                rec.period_text = False

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        index=True,
        required=True,
        domain="[('area','=',area_id),('branch_id','=',branch_id),('state','=','approved')]"
    )

    work_unit_ids = fields.Many2many(
        'mst.group.unit.pelayanan',  string='Work Unit',  compute='_compute_work_unit_ids', store=True)

    @api.depends('employee_id.work_unit_ids')
    def _compute_work_unit_ids(self):
        for rec in self:
            rec.work_unit_ids = rec.employee_id.work_unit_ids

    nik = fields.Char(related='employee_id.nik',
                      string='NIK', store=True, readonly=True)
    employee_name = fields.Char(
        related='employee_id.name', string='Employee Name', index=True, readonly=True)
    branch_id = fields.Many2one(related='employee_id.branch_id', string='Bisnis Unit',
                                store=True, index=True, readonly=True, default=lambda self: self.env.user.branch_id.id)
    area_id = fields.Many2one(related='employee_id.area', string='Area ID', store=True,
                              index=True, readonly=True, default=lambda self: self.env.user.branch_id.territory_id.id)
    directorate_id = fields.Many2one(
        related='employee_id.directorate_id', string='Direktorat', store=True, index=True, readonly=True)
    hrms_department_id = fields.Many2one(
        related='employee_id.hrms_department_id', string='Departemen', store=True, index=True, readonly=True)
    division_id = fields.Many2one(
        related='employee_id.division_id', string='Divisi', store=True, index=True, readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id',
                                    string='Sub Department', store=True, index=True, readonly=True)
    job_id = fields.Many2one(related='employee_id.job_id',
                             string='Job Position', store=True, index=True, readonly=True)
    jabatan = fields.Char(related='job_id.name', string='Jabatan',
                          store=True, index=True, readonly=True)

    is_select = fields.Boolean(default=False)

    date_21 = fields.Many2one('hr.working.days', string='21',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_21 = fields.Float(
    #     '21', related='date_21.total_working_hours', store=False)
    date_22 = fields.Many2one('hr.working.days', string='22',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_22 = fields.Float(
    #     '22', related='date_22.total_working_hours', store=False)
    date_23 = fields.Many2one('hr.working.days', string='23',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_23 = fields.Float(
    #     '23', related='date_23.total_working_hours', store=False)
    date_24 = fields.Many2one('hr.working.days', string='24',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_24 = fields.Float(
    #     '24', related='date_24.total_working_hours', store=False)
    date_25 = fields.Many2one('hr.working.days', string='25',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_25 = fields.Float(
    #     '25', related='date_25.total_working_hours', store=False)
    date_26 = fields.Many2one('hr.working.days', string='26',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_26 = fields.Float(
    #     '26', related='date_26.total_working_hours', store=False)
    date_27 = fields.Many2one('hr.working.days', string='27',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_27 = fields.Float(
    #     '27', related='date_27.total_working_hours', store=False)
    date_28 = fields.Many2one('hr.working.days', string='28',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_28 = fields.Float(
    #     '28', related='date_28.total_working_hours', store=False)
    date_29 = fields.Many2one('hr.working.days', string='29',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_29 = fields.Float(
    #     '29', related='date_29.total_working_hours', store=False)
    date_30 = fields.Many2one('hr.working.days', string='30',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_30 = fields.Float(
    #     '30', related='date_30.total_working_hours', store=False)
    date_31 = fields.Many2one('hr.working.days', string='31',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_31 = fields.Float(
    #     '01', related='date_31.total_working_hours', store=False)
    date_01 = fields.Many2one('hr.working.days', string='01',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_01 = fields.Float(
    #     '02', related='date_01.total_working_hours', store=False)
    date_02 = fields.Many2one('hr.working.days', string='02',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_02 = fields.Float(
    #     '02', related='date_02.total_working_hours', store=False)
    date_03 = fields.Many2one('hr.working.days', string='03',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_03 = fields.Float(
    #     '03', related='date_03.total_working_hours', store=False)
    date_04 = fields.Many2one('hr.working.days', string='04',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_04 = fields.Float(
    #     '04', related='date_04.total_working_hours', store=False)
    date_05 = fields.Many2one('hr.working.days', string='05',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_05 = fields.Float(
    #     '05', related='date_05.total_working_hours', store=False)
    date_06 = fields.Many2one('hr.working.days', string='06',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_06 = fields.Float(
    #     '06', related='date_06.total_working_hours', store=False)
    date_07 = fields.Many2one('hr.working.days', string='07',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_07 = fields.Float(
    #     '07', related='date_07.total_working_hours', store=False)
    date_08 = fields.Many2one('hr.working.days', string='08',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_08 = fields.Float(
    #     '08', related='date_08.total_working_hours', store=False)
    date_09 = fields.Many2one('hr.working.days', string='09',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_09 = fields.Float(
    #     '09', related='date_09.total_working_hours', store=False)
    date_10 = fields.Many2one('hr.working.days', string='10',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_10 = fields.Float(
    #     '10', related='date_10.total_working_hours', store=False)
    date_11 = fields.Many2one('hr.working.days', string='11',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_11 = fields.Float(
    #     '11', related='date_11.total_working_hours', store=False)
    date_12 = fields.Many2one('hr.working.days', string='12',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_12 = fields.Float(
    #     '12', related='date_12.total_working_hours', store=False)
    date_13 = fields.Many2one('hr.working.days', string='13',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_13 = fields.Float(
    #     '13', related='date_13.total_working_hours', store=False)
    date_14 = fields.Many2one('hr.working.days', string='14',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_14 = fields.Float(
    #     '14', related='date_14.total_working_hours', store=False)
    date_15 = fields.Many2one('hr.working.days', string='15',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_15 = fields.Float(
    #     '15', related='date_15.total_working_hours', store=False)
    date_16 = fields.Many2one('hr.working.days', string='16',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_16 = fields.Float(
    #     '16', related='date_16.total_working_hours', store=False)
    date_17 = fields.Many2one('hr.working.days', string='17',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_17 = fields.Float(
    #     '17', related='date_17.total_working_hours', store=False)
    date_18 = fields.Many2one('hr.working.days', string='18',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_18 = fields.Float(
    #     '18', related='date_18.total_working_hours', store=False)
    date_19 = fields.Many2one('hr.working.days', string='19',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_19 = fields.Float(
    #     '19', related='date_19.total_working_hours', store=False)
    date_20 = fields.Many2one('hr.working.days', string='20',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False),('type_hari','!=','fhday')]")
    # hours_20 = fields.Float(
    #     '20', related='date_20.total_working_hours', store=False)

    active = fields.Boolean(default=True, string='Active')
    state = fields.Selection(
        selection=TMS_ENTRY_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    approved_by = fields.Many2one('res.users', string="Approved By")
    approved_date = fields.Date(string="Approved Date")
    review_by = fields.Many2one('res.users', string="Reviewd by")
    review_date = fields.Date(string="Reviewd Date")
    name = fields.Char(string='Reference', index=True,
                       compute='_compute_display_name', store=True)
    reason = fields.Char(
        string='Reason', help='Reason for setting the record to draft.')

    profesion = fields.Char(
        'Profesi',
        index=True,
        store=True,
        help='Profesion of Employee.')

    group_shift = fields.Char(string="Group Shift", store=True)
    total_working_hours = fields.Float(
        'Total Working Hours', store=True,
        compute='_compute_total_working_hours',
        help='Total working hours in the shift period.')

    @api.depends(
        'date_21', 'date_22', 'date_23', 'date_24', 'date_25', 'date_26', 'date_27', 'date_28', 'date_29', 'date_30', 'date_31',
        'date_01', 'date_02', 'date_03', 'date_04', 'date_05', 'date_06', 'date_07', 'date_08', 'date_09', 'date_10',
        'date_11', 'date_12', 'date_13', 'date_14', 'date_15', 'date_16', 'date_17', 'date_18', 'date_19', 'date_20'
    )
    def _compute_total_working_hours(self):
        # List semua field tanggal yang ada di form
        date_fields = [
            'date_21', 'date_22', 'date_23', 'date_24', 'date_25', 'date_26', 'date_27', 'date_28', 'date_29', 'date_30', 'date_31',
            'date_01', 'date_02', 'date_03', 'date_04', 'date_05', 'date_06', 'date_07', 'date_08', 'date_09', 'date_10',
            'date_11', 'date_12', 'date_13', 'date_14', 'date_15', 'date_16', 'date_17', 'date_18', 'date_19', 'date_20'
        ]

        for rec in self:
            total_hours = 0.0
            for field in date_fields:
                working_day = rec[field]
                if working_day:
                    duration = working_day.total_working_hours
                    if duration > 0:
                        total_hours += duration

            rec.total_working_hours = total_hours

    shift_id = fields.Many2one(
        'sb.group.shift', string='Group Shift', index=True,)

    # work_unit_ids = fields.Many2many(
    #     'mst.group.unit.pelayanan',  string='Work Unit',  compute='_compute_work_unit_ids', store=True)

    # @api.depends('employee_id.work_unit_ids')
    # def _compute_work_unit_ids(self):
    #     for rec in self:
    #         rec.work_unit_ids = rec.employee_id.work_unit_ids

    display_name = fields.Char(
        string='Display Name', index=True, compute='_compute_display_name', store=True)

    _sql_constraints = [
        (
            'unique_employee_per_period',
            'UNIQUE(periode_id, employee_id,active)',
            'Karyawan sudah memiliki data shift untuk periode ini.'
        )
    ]

    @api.depends('employee_name', 'period_text')
    def _compute_display_name(self):
        """Menghitung Display Name dan menyimpan Reference Name."""
        for record in self:
            employee_name = (record.employee_name or '').upper()
            period_text = (record.period_text or '').upper()
            if employee_name and period_text:
                full_name = f"{employee_name} - {period_text}"
                record.display_name = full_name
                record.name = full_name
            else:
                record.display_name = employee_name or 'New'
                record.name = employee_name or 'New'

    def action_review(self):
        """Mengubah status menjadi Review."""
        for rec in self:
            if rec.state != 'draft' or not rec.active:
                raise UserError(
                    _("Entri shift harus dalam status 'Draft' dan 'Active' untuk dikirim ke Review."))
        return self.write({'state': 'review',
                           'review_by': self.env.user.id,
                           'review_date': datetime.today()
                           })

    def action_approve(self):
        """Mengubah status menjadi Approved."""
        for rec in self:
            if rec.state != 'review' or not rec.active:
                raise UserError(
                    _("Entri shift harus dalam status 'HRD Review' dan 'Active' untuk Disetujui."))
        return self.write({'state': 'approved',
                           'approved_by': self.env.user.id,
                           'reason': False,
                           'approved_date': datetime.today()})

    def action_detail_summary(self):
        for rec in self:
            summary_id = self.env['hr.tmsentry.summary'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('periode_id', '=', rec.periode_id.id)
            ])
            if not summary_id:
                raise UserError(
                    _("Data record tidak ada, silahkan hubungi HRD untuk menjalankan processing and period periode tersebut.")
                )
            try:
                view_id = self.env.ref(
                    'sanbe_hr_tms.hr_tmsentry_summary_shift').id
            except ValueError:
                raise UserError(
                    _("View hr_tmsentry_summary_shift tidak ditemukan.")
                )

            return {
                'type': 'ir.actions.act_window',
                'name': 'hr.tmsentry.summary',
                'view_mode': 'form',
                'res_model': 'hr.tmsentry.summary',
                'view_id': view_id,  # Menggunakan ID view yang ditemukan
                'res_id': summary_id.id,
                'target': 'new',
                'context': {'create': False, 'delete': False, 'edit': False},
            }

        return True
    # def action_reject(self):
    #     """Mengubah status menjadi Reject."""
    #     for rec in self:
    #         if rec.state in ('approved', 'reject') or not rec.active:
    #             raise UserError(_("Entri shift sudah 'Approved' atau 'Rejected' atau Inactive. Tidak dapat diubah statusnya."))
    #     return self.write({'state': 'reject'})

    def action_set_to_draft(self):
        """Mengubah status kembali menjadi Draft."""
        for rec in self:
            if rec.state != 'draft':
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Kembalikan ke Draft',
                    'res_model': 'wiz.hr.set.draft',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_target_models': 'sb.employee.shift',
                        'default_shift_id': rec.id,
                    }}

                # rec.write({'state': 'draft',
                #            'approved_by': False,
                #            'approved_date': False,
                #            'review_by': False,
                #            'review_date': False})

        # return True

    def action_delete(self):
        for record in self:
            record.unlink()

    def action_mass_review(self):
        current_branch_id = self.env.user.branch_id.id
        # approve per branch jika diperlukan
        valid_records = self.filtered(
            lambda r: r.branch_id.id == current_branch_id)
        if valid_records:
            invalid_state = valid_records.filtered(
                lambda r: r.state != 'draft')
            if invalid_state:
                names = ', '.join(invalid_state.mapped('display_name'))
                raise UserError(
                    f'Tidak bisa approve, beberapa record tidak dalam state Submit: {names}')
            valid_records.write({
                'state': 'review',
                'review_by': self.env.user.id,
                'review_date': datetime.today()
            })

    def action_mass_approve(self):
        """ 
        Filter by branch and check when it's not review sementara di non aktifkan
        """
        valid_records = self
        if valid_records:
            valid_records.write({
                'state': 'approved',
                'review_by': self.env.user.id,
                'review_date': datetime.today(),
                'approved_by': self.env.user.id,
                'approved_date': datetime.today()
            })
