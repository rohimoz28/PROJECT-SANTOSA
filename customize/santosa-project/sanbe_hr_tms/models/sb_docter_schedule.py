from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import pytz
from datetime import datetime, time, timedelta
import logging

_logger = logging.getLogger(__name__)

DOcter_status = [
    ('draft', 'Draft'),
    ('verified', "Verified By L1"),
    ('approved', 'Approved By HRD'),
    ('complete', "Complete By HCM"),
    ('done', "Close"),
    ('reject', "Reject"),
]


class SbDocterScheduling(models.Model):
    _name = 'sb.docter.scheduling'
    _description = 'Doctor Scheduling'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin', 'utm.mixin']

    def _get_running_periode(self):
        """Mendapatkan periode 'running'/'draft' yang aktif untuk Branch pengguna saat ini."""
        user_branch_id = self.env.user.branch_id.id
        if not user_branch_id:
            return False
        base_domain = [
            ('branch_id', '=', user_branch_id),
            ('state_process', 'in', ['draft', 'running'])
        ]
        active_domain = base_domain + [
            ('open_periode_from', '<=', fields.Datetime.now()),
            ('open_periode_to', '>=', fields.Datetime.now())
        ]
        periode = self.env['hr.opening.closing'].search(
            active_domain,
            order='open_periode_from desc',
            limit=1
        )
        if not periode:
            periode = self.env['hr.opening.closing'].search(
                base_domain,
                order='open_periode_from desc',
                limit=1
            )
        return periode.id if periode else False

    area_id = fields.Many2one(
        "res.territory",
        string='Area ID',
        copy=True,
        index=True,
        default=lambda self: self.env.user.area.id,
        tracking=True
    )
    branch_id = fields.Many2one(
        'res.branch',
        string='Bisnis Unit',
        copy=True,
        index=True,
        default=lambda self: self.env.user.branch_id.id,
        tracking=True
    )

    name = fields.Char(
        'Dokter Name', related='employee_id.name', store=True, index=True)
    jadwal_id = fields.Char('Jadwal Id', index=True)

    periode_id = fields.Many2one('hr.opening.closing', string='Period',
                                 domain="[('branch_id','=',branch_id),('state_process','in',('draft','running'))]", index=True,
                                 default=_get_running_periode)
    employee_id = fields.Many2one(
        'hr.employee', 'Dokter', domain="[('employee_category','=','dokter')]", index=True)
    emp_id = fields.Char(
        'Employee ID', related='employee_id.employee_id', index=True)
    specialization = fields.Char(
        'Specialisation', related='sip_id.specialization', readonly=True, store=True)
    employee_nik = fields.Char('NIK', related='employee_id.nik', store=True)
    job_status = fields.Selection(
        related='employee_id.job_status', string="Status Hub Kerja")
    emp_status_id = fields.Many2one(
        'hr.emp.status', related='employee_id.emp_status_id', string="Status Hub Kekaryawanan")
    sip_id = fields.Many2one(
        'hr.sip', domain="[('employee_id','=',employee_id),('state','=','open')]", string="No SIP", store=True)
    status = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')], default='active')
    active = fields.Boolean(default=True)
    start_date = fields.Date(string='Berlaku Dari',
                             related="sip_id.start_date", required=True)
    end_date = fields.Date(string='Berlaku Hingga',
                           related="sip_id.end_date", required=True)
    line_ids = fields.One2many('sb.docter.scheduling.detail',
                               'scheduling_id', string='Schedule Lines', tracking=True)
    state = fields.Selection(DOcter_status, readonly=True,
                             copy=False, index=True, tracking=True, default='draft')
    _sql_constraints = [(
        'unique_number',
        'unique(periode_id, employee_id,sip_id)',
        'Dokter tersebut dg SIP tersebut sudah terdaftar.'
    )]

    @api.onchange('employee_id')
    def _get_sip_default(self):
        for line in self:
            if line.employee_id:
                for sip in self.env['hr.sip'].search([('employee_id', '=', line.employee_id.id), ('state', '=', 'open')], limit=1):
                    if not sip:
                        raise UserError('Dokter tersebut belum memiliki SIP')
                    else:
                        line.sip_id = sip.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                branch_unit_id = self.env.user.branch_id.unit_id
                branch_code = self.env.user.branch_id.branch_code
                tgl = fields.Date.today()
                tahun = str(tgl.year)[2:]
                bulan = str(tgl.month)
                sequence_code = self.env['ir.sequence'].next_by_code(
                    'sb.docter.scheduling')
                vals['jadwal_id'] = f"{tahun}/{bulan}/{branch_unit_id}/{branch_code}/{sequence_code}"
        return super().create(vals_list)

    @api.constrains('employee_id')
    def _check_sip_dokter(self):
        if not self.employee_id.sip:
            raise UserError('Doker Belum dibuatkan SIP')

    @api.depends('employee_id')
    def _set_default_sip(self):
        for line in self:
            line.sip_id = self.env['hr.sip'].search(
                [('employee_id', '=', line.employee_id.id), ('state', '=', 'open')], limit=1).id

    @api.onchange('status')
    def _onchange_status(self):
        self.active = self.status == 'active'

    # @api.depends('employee_id')
    # def _get_specialisation(self):
    #     for record in self:
    #         query = """
    #             select specialization  from hr_sip hs where hs.specialization
    #             is not null and state = 'open' where employee_id =%s
    #         """
    #         self._cr.execute(query,(self.employee_id.id))
    #         sip_data = self._cr.fetchall()
    #         if sip_data:
    #             specializations = [temp[0] for temp in sip_data]
    #             if len(specializations) > 1:
    #                 record.specialisation = "\n".join(specializations)
    #             else:
    #                 record.specialisation = specializations[0]
    #         else:
    #             record.specialisation = False

    def btn_print_pdf(self):
        pass

    def btn_verified(self):
        for rec in self:
            rec.state = 'verified'

    def btn_approved(self):
        for rec in self:
            rec.state = 'approved'

    def btn_done(self):
        for rec in self:
            rec.state = 'done'

    def btn_complete(self):
        for rec in self:
            rec.state = 'complete'

    def btn_reject(self):
        for rec in self:
            rec.state = 'reject'

    def btn_backdraft(self):
        for rec in self:
            rec.state = 'draft'


class SbDocterSchedulingDetail(models.Model):
    _name = 'sb.docter.scheduling.detail'
    _description = 'Doctor Scheduling Detail'

    scheduling_id = fields.Many2one(
        'sb.docter.scheduling', string='Scheduling', ondelete='cascade')
    branch_id = fields.Many2one(
        'res.branch',
        string='Bisnis Unit',
        copy=True, required=True,
        index=True,
        default=lambda self: self.env.user.branch_id.id,
        tracking=True
    )
    name = fields.Char('Hari Praktek', compute='_compute_name', store=True)
    sip_id = fields.Many2one(readonly=True, related='scheduling_id.sip_id')
    hari = fields.Selection([
        ('monday', 'Senin'),
        ('tuesday', 'Selasa'),
        ('wednesday', 'Rabu'),
        ('thursday', 'Kamis'),
        ('friday', 'Jumat'),
        ('saturday', 'Sabtu'),
        ('sunday', 'Minggu'),
    ], string="Hari", required=True)
    start_hours = fields.Float(
        string='Jam Mulai', default=lambda self: self._get_default_start_hours(), required=True)
    end_hours = fields.Float(
        string='Jam Selesai', default=lambda self: self._get_default_end_hours(), required=True)
    status = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')], default='active', required=True)

    # Method untuk mengisi field name dengan nama hari yang sesuai

    @api.depends('hari')
    def _compute_name(self):
        for record in self:
            if record.hari:
                record.name = dict(
                    record._fields['hari'].selection).get(record.hari)
            else:
                record.name = False

    @api.constrains('start_hours', 'end_hours')
    def _check_time_range(self):
        for record in self:
            if not record.start_hours or not record.end_hours:
                continue

            if not (0.0 <= record.start_hours <= 24.0 and
                    0.0 <= record.end_hours <= 24.0):
                raise UserError("Waktu harus dalam rentang 0.0 hingga 24.0.")
            if record.start_hours >= record.end_hours:
                raise UserError(
                    "Jam praktek 'mulai' harus lebih awal dari jam praktek 'Selesai'.")

    def _get_default_start_hours(self):
        if self.scheduling_id and self.scheduling_id.sip_id:
            return self.scheduling_id.sip_id.work_start
        return 0.0

    def _get_default_end_hours(self):
        if self.scheduling_id and self.scheduling_id.sip_id:
            return self.scheduling_id.sip_id.work_end
        return 0.0

    @api.model_create_multi
    def create(self, values):
        if 'sip_id' in values:
            sip = self.env['hr.sip'].browse(values['sip_id'])
            if sip:
                values['start_hours'] = sip.work_start
                values['end_hours'] = sip.work_end
        return super().create(values)

    def _convert_float_to_time(self, hours_float):
        hours = int(hours_float)
        minutes = int((hours_float - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    @api.depends('hari', 'start_hours', 'start_hours')
    def _compute_display_name(self):
        for account in self:
            account.display_name = '%s %s - %s' % (account.name, self._convert_float_to_time(
                account.start_hours) or '00:00', self._convert_float_to_time(account.start_hours) or '00:00')
