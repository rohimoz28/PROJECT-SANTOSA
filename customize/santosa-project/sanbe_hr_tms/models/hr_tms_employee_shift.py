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
    _order = "periode_id desc, directorate_id asc, hrms_department_id asc, division_id asc, jabatan asc"

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
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_22 = fields.Many2one('hr.working.days', string='22',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_23 = fields.Many2one('hr.working.days', string='23',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_24 = fields.Many2one('hr.working.days', string='24',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_25 = fields.Many2one('hr.working.days', string='25',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_26 = fields.Many2one('hr.working.days', string='26',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_27 = fields.Many2one('hr.working.days', string='27',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_28 = fields.Many2one('hr.working.days', string='28',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_29 = fields.Many2one('hr.working.days', string='29',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_30 = fields.Many2one('hr.working.days', string='30',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_31 = fields.Many2one('hr.working.days', string='31',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_01 = fields.Many2one('hr.working.days', string='01',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_02 = fields.Many2one('hr.working.days', string='02',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_03 = fields.Many2one('hr.working.days', string='03',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_04 = fields.Many2one('hr.working.days', string='04',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_05 = fields.Many2one('hr.working.days', string='05',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_06 = fields.Many2one('hr.working.days', string='06',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_07 = fields.Many2one('hr.working.days', string='07',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_08 = fields.Many2one('hr.working.days', string='08',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_09 = fields.Many2one('hr.working.days', string='09',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_10 = fields.Many2one('hr.working.days', string='10',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_11 = fields.Many2one('hr.working.days', string='11',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_12 = fields.Many2one('hr.working.days', string='12',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_13 = fields.Many2one('hr.working.days', string='13',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_14 = fields.Many2one('hr.working.days', string='14',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_15 = fields.Many2one('hr.working.days', string='15',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_16 = fields.Many2one('hr.working.days', string='16',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_17 = fields.Many2one('hr.working.days', string='17',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_18 = fields.Many2one('hr.working.days', string='18',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_19 = fields.Many2one('hr.working.days', string='19',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    date_20 = fields.Many2one('hr.working.days', string='20',
                              domain="['|',('available_for','in',branch_id),('available_for','=',False)]")

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
