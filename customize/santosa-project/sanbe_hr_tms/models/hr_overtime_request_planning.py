# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
from email.policy import default

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import pytz
from datetime import datetime, time, timedelta
from math import ceil, floor
import logging

_logger = logging.getLogger(__name__)

TMS_OVERTIME_STATE = [
    ('draft', 'Draft'),
    ('approved_l1', "Approved L1"),
    ('approved_l2', "Approved L2"),
    ('verified', "Verified By L1"),
    ('approved', 'Approved By HRD'),
    ('complete', "Complete By HCM"),
    ('done', "Close"),
    ('reject', "Reject"),
]

OT_HOURS_SELECTION = [
    ('h_morning', "H - Lembur Pagi"),
    ('h_afternoon', "H - Lembur Siang"),
    ('h_night', "H - Lembur Malam"),
    ('r_s1', "R - Shift 1"),
    ('r_s2', "R - Shift 2"),
    ('r_s3', "R - Shift 3"),
    ('others', "Others"),
]


class HREmpOvertimeRequest(models.Model):
    _name = "hr.overtime.planning"
    _description = 'HR Employee Overtime Planning Request'
    _rec_name = 'name'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin', 'utm.mixin']

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search(
                    [('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search(
                [('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area_id', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            allbranch = self.env['hr.department'].sudo().search(
                [('branch_id', '=', allrecs.branch_id.id)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]

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

    name = fields.Char('Nomor Surat Perintah Lembur', default=lambda self: _('New'),
                       copy=False, readonly=True, tracking=True, requirement=True)
    request_date = fields.Date(
        'Tanggal Surat Perintah Lembur', default=fields.Date.today(), readonly=True)

    area_id = fields.Many2one(
        "res.territory",
        string='Area ID',
        copy=True,
        index=True,
        default=lambda self: self.env.user.area.id,
        tracking=True
    )
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)

    current_user_employee_id_ref = fields.Integer(
        string='Current User Employee ID',
        default=lambda self: self.env.user.employee_id.id if self.env.user.employee_id else 0,
        store=False,  # Tidak perlu disimpan di database
    )

    # is_approver = fields.Selection([('manager', 'Manager'), ('approver', 'Approver'), ('staff', 'Staff')],
    #                                default=lambda self: self._compute_approver(), store=False)

    is_approver = fields.Selection(
        [
            ('manager', 'Manager'),
            ('approver', 'Approver'),
            ('staff', 'Staff'),
        ],
        default=lambda self: self._compute_is_approver(),
        store=False,
    )

    def _compute_is_approver(self):
        """ Always compute based on current logged user """
        user = self.env.user
        is_approver = 'staff'  # Default role
        if user.has_group('sanbe_hr_tms.module_surat_perintah_lembur_approver'):
            is_approver = 'approver'
        elif user.has_group('sanbe_hr_tms.module_surat_perintah_lembur_manager'):
            is_approver = 'manager'
        else:
            is_approver = 'staff'
        return is_approver

    branch_id = fields.Many2one(
        'res.branch',
        string='Bisnis Unit',
        copy=True,
        index=True,
        default=lambda self: self.env.user.branch_id.id,
        tracking=True
    )
    alldepartment = fields.Many2many('hr.department', 'hr_department_plan_ot_rel', string='All Department',
                                     compute='_isi_department_branch', store=False)
    department_id = fields.Many2one(
        'hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    division_id = fields.Many2one('sanhrms.division', string='Divisi',
                                  default=lambda self: self.env.user.employee_id.division_id.id,
                                  domain="[('hrms_department_id','=',hrms_department_id)]", store=True)
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen',
                                         default=lambda self: self.env.user.employee_id.hrms_department_id.id,
                                         domain="[('directorate_id','=',directorate_id)]", store=True)
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat',
                                     default=lambda self: self.env.user.employee_id.directorate_id.id,
                                     domain="['|',('branch_id','=',branch_id),('branch_id','=',False)]", store=True)
    periode_from = fields.Date(
        'Perintah Lembur Dari', default=fields.Date.today)
    used_at = fields.Date(
        'Digunakan Pada', default=fields.Date.today)
    job_id = fields.Many2one('hr.job', string='Jabatan',
                             related='employee_id.job_id', store=True)
    emp_level = fields.Many2one(
        'employee.level', string='Level Karyawan', related='employee_id.employee_levels', store=True)
    periode_to = fields.Date('Hingga', default=fields.Date.today)
    approve1 = fields.Boolean('Approval L1', default=False)
    approve2 = fields.Boolean('Approval L2', default=False)
    approve3 = fields.Boolean('Approval by HCM', default=False)
    state = fields.Selection(
        selection=TMS_OVERTIME_STATE,
        string="TMS Overtime Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft')
    periode_id = fields.Many2one('hr.opening.closing', string='Period',
                                 domain="[('branch_id','=',branch_id),('state','in',('draft','running'))]", index=True,
                                 default=_get_running_periode)
    hr_ot_planning_ids = fields.One2many('hr.overtime.employees', 'planning_id', auto_join=True, index=True,
                                         required=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan',
                                  domain="[('state','=','approved'),('division_id','=',division_id),'|',"
                                         "('branch_id','=',branch_id),('branch_id','=',False)]",
                                  store=True, track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', string="Company Name", index=True)
    total_days = fields.Float(
        string="Total hari", compute='_compute_get_total_days_hours', store=True, )
    total_hours = fields.Float(
        string="Total Jam", compute='_compute_get_total_days_hours', store=True, )
    day_payment = fields.Boolean('Day Payment', default=False, store=True, )
    request_day_name = fields.Char(
        'Request Day Name', compute='_compute_req_day_name', store=True)
    count_record_employees = fields.Integer(string="Total Employees on The List", compute="_compute_record_employees",
                                            store=True)
    # approverhrd_id = fields.Many2one('hr.employee', string='Approval by HRD',
    #                                  domain="[('branch_id','=',branch_id), ('hrms_department_id', 'in',  [97, 174, 235]), ('user_id','!=', False)]",
    #                                  store=True, index=True)
    approverhrd_id = fields.Many2one('hr.employee', string='Approval by HRD',
                                     domain="[('branch_id','=',branch_id),('hrms_department_id','=',approval_dept), ('user_id','!=', False)]",
                                     store=True, index=True)

    approval_dept = fields.Many2one(
        'sanhrms.department', string='Departemen',
        compute='_compute_approval_dept',
        store=True)

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     if not self.branch_id:
    #         self.approval_dept = False
    #         return
    #
    #     param = self.env['ir.config_parameter'].sudo().get_param('SPLHRD')
    #     if param:
    #         # Membersihkan spasi dan memastikan hanya angka
    #         department_ids = [int(x.strip())
    #                           for x in param.split(',') if x.strip().isdigit()]
    #     else:
    #         department_ids = []
    #
    #     if not department_ids:
    #         # Sebaiknya jangan raise UserError di onchange karena mengganggu user saat mengetik
    #         # Cukup kosongkan saja atau beri peringatan log
    #         self.approval_dept = False
    #         return
    #
    #     approval_dept_rec = self.env['sanhrms.department'].search([
    #         ('id', 'in', department_ids),
    #         ('branch_id', '=', self.branch_id.id)
    #     ], limit=1)
    #
    #     if approval_dept_rec:
    #         # CARA PERBAIKAN: Masukkan nilai ke field, bukan di-return
    #         self.approval_dept = approval_dept_rec.id
    #     else:
    #         self.approval_dept = False
    #         # Opsional: return warning jika ingin memunculkan popup tanpa error keras
    #         return {'warning': {
    #             'title': "Data Tidak Ditemukan",
    #             'message': "Approval HRD untuk cabang ini belum diatur."
    #         }}

    @api.model
    def _get_splhrd_ids(self):
        """Fetch the list of HRD department IDs from system parameter"""
        # param = self.env['ir.config_parameter'].sudo().get_param('hr.overtime.planning')
        param = self.env['ir.config_parameter'].sudo().get_param('SPLHRD')
        return [int(x) for x in param.split(',')] if param else []

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        """Set approval_dept dan domain untuk approverhrd_id berdasarkan branch_id"""
        if not self.branch_id:
            self.approval_dept = False
            return

        # Ambil parameter SPLHRD
        param = self.env['ir.config_parameter'].sudo().get_param('SPLHRD')
        if param:
            department_ids = [int(x.strip())
                              for x in param.split(',') if x.strip().isdigit()]
        else:
            department_ids = []

        # Set approval_dept
        if department_ids:
            approval_dept_rec = self.env['sanhrms.department'].search([
                ('id', 'in', department_ids),
                ('branch_id', '=', self.branch_id.id)
            ], limit=1)

            if approval_dept_rec:
                self.approval_dept = approval_dept_rec.id
            else:
                self.approval_dept = False
                return {'warning': {
                    'title': "Data Tidak Ditemukan",
                    'message': "Approval HRD untuk cabang ini belum diatur."
                }}
        else:
            self.approval_dept = False

        # Set domain untuk approverhrd_id
        return {
            'domain': {
                'approverhrd_id': [
                    ('branch_id', '=', self.branch_id.id),
                    ('hrms_department_id', 'in', department_ids),
                    ('user_id', '!=', False),
                ]
            }
        }

    @api.depends('branch_id')
    def _compute_approval_dept(self):
        """Compute approval_dept dari branch_id"""
        for rec in self:
            if not rec.branch_id:
                rec.approval_dept = False
                continue

            param = self.env['ir.config_parameter'].sudo().get_param('SPLHRD')
            if not param:
                rec.approval_dept = False
                continue

            try:
                department_ids = [int(x.strip())
                                  for x in param.split(',') if x.strip().isdigit()]
            except (ValueError, AttributeError):
                rec.approval_dept = False
                continue

            if not department_ids:
                rec.approval_dept = False
                continue

            approval_dept_rec = self.env['sanhrms.department'].search([
                ('id', 'in', department_ids),
                ('branch_id', '=', rec.branch_id.id)
            ], limit=1)

            rec.approval_dept = approval_dept_rec.id if approval_dept_rec else False

    approval_l1_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approval L1',
        compute='_get_approver_l1_l2',
        store=True,
        required=False)
    approval_l2_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approval L2',
        compute='_get_approver_l1_l2',
        store=True,
        required=False)
    can_approve_l1 = fields.Boolean(
        string='Can Approve L1',
        compute='_compute_can_approve_l1',
        help='Check if current user can approve as Atasan')
    can_approve_l2 = fields.Boolean(
        string='Can Approve L2',
        compute='_compute_can_approve_l2',
        help='Check if current user can approve as Atasan Unit Kerja')
    can_verified = fields.Boolean(
        string='Can Verified',
        compute='_compute_can_verified',
        help='Check if current user can verified')
    can_approve_hrd = fields.Boolean(
        string='Can Approve HRD',
        compute='_compute_can_approve_hrd',
        help='Check if current user can approve as HRD')

    @api.constrains('approval_l1_id')
    def _check_approval_l1_has_user(self):
        """Validate Approver L1 memiliki user login"""
        for record in self:
            if record.approval_l1_id and not record.approval_l1_id.user_id:
                raise UserError(
                    f'Approver L1 ({record.approval_l1_id.name}) '
                    f'belum memiliki user login. '
                    f'Silakan hubungi Administrator untuk mengatur user login.'
                )

    @api.constrains('approval_l2_id')
    def _check_approval_l2_has_user(self):
        """Validate Approver L2 memiliki user login"""
        for record in self:
            if record.approval_l2_id and not record.approval_l2_id.user_id:
                raise UserError(
                    f'Approver L2 ({record.approval_l2_id.name}) '
                    f'belum memiliki user login. '
                    f'Silakan hubungi Administrator untuk mengatur user login.'
                )

    @api.depends('hr_ot_planning_ids.is_select', 'hr_ot_planning_ids.adv_total_ot')
    def _compute_get_total_days_hours(self):
        """Menghitung total hari dan jam berdasarkan detail lembur yang dipilih."""
        for rec in self:
            total_days = 0.0
            total_hours = 0.0
            for line in rec.hr_ot_planning_ids:
                if line.is_select:
                    total_hours += line.residual_ot
                    total_days += 1
            if total_hours >= 7:
                rec.total_hours = 7
                rec.total_days = total_days
            else:
                rec.total_hours = total_hours
                rec.total_days = total_days

    @api.constrains('approverhrd_id')
    def _check_approverhrd_has_user(self):
        """Validate Approver HRD memiliki user login"""
        for record in self:
            if record.approverhrd_id and not record.approverhrd_id.user_id:
                raise UserError(
                    f'Approver HRD ({record.approverhrd_id.name}) '
                    f'belum memiliki user login. '
                    f'Silakan hubungi Administrator untuk mengatur user login.'
                )

    """
    Untuk menentukan user mana saja yang boleh klik button approval
    Dibuatlah compute method :  
    
        |  Compute Method          | Field           |
        | -------------------------|-----------------|        
        |  _compute_can_approve_l1 | can_approve_l1  |
        |  _compute_can_approve_l2 | can_approve_l2  |
        |  _compute_can_verified   | can_verified    |
        |  _compute_can_approve_hrd| can_approve_hrd |
        
    Pada method compute tersebut dibuatlah validasi yang jika lolos , maka akan mengembalikan nilai TRUE
    Lalu pada view XML, compute field akan dijadikan kondisi pada attribute invisible. (eg. invisible="not can_approve_l2")
    
    Dengan cara ini, bisa menghindari kerumitan jika menggunakan teknik overriding method bawaan odoo : _get_view()
    Namun, tetap memiliki fleksibilitas tinggi terhadap requirement kondisi yang dibutuhkan.
    """

    @api.depends('state', 'approval_l1_id')
    def _compute_can_approve_l1(self):
        """
        Button Approve (Atasan) muncul jika:
        1. State = draft
        2. Field approval_l1_id ada isinya
        3. Current user == approval_l1_id (atasan)
        """
        current_user = self.env.user

        for rec in self:
            can_approve = (
                    rec.state == 'draft'
                    and not rec.approve1
                    and rec.approval_l1_id
                    and rec.approval_l1_id.user_id.id == current_user.id
            )
            rec.can_approve_l1 = can_approve

    @api.depends('state', 'approval_l2_id')
    def _compute_can_approve_l2(self):
        """
        Button Approve (Atasan Unit Kerja) muncul jika:
        1. State = approved_atasan
        2. Current user = approval_l2_id (Atasan Unit Kerja)
        3. Field approval_l2_id ada isinya && Sudah di approve oleh approval_l1_id
        """
        current_user = self.env.user

        for rec in self:
            can_approve = (
                    rec.state == 'approved_l1'
                    and rec.approve1
                    and not rec.approve2
                    and rec.approval_l2_id
                    and rec.approval_l2_id.user_id.id == current_user.id
            )
            rec.can_approve_l2 = can_approve

    @api.depends('state', 'employee_id', )
    def generate_list_ot_employee(self):
        for rec in self:
            if rec.employee_id:
                for line_ot in self.env['hr.overtime.employees'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('state', 'in',
                                                                          ('verified', 'approved', 'complete',
                                                                           'done'))]):
                    line_ot.unlink()

    @api.depends('state', 'approval_l1_id', 'approval_l2_id')
    def _compute_can_verified(self):
        """
        Button Verified muncul jika:
        1. State = approved_l2
        2. Current user = approval_l1_id (atasan langsung)
        3. Field approval_l1_id && approval_l2_id ada isinya
        4. Sudah di approve oleh approval_l1_id && approval_l2_id
        """
        current_user = self.env.user

        for rec in self:
            can_approve = (
                    rec.state == 'approved_l2'
                    and rec.approval_l1_id
                    and rec.approve1
                    and rec.approval_l2_id
                    and rec.approve2
                    and rec.approval_l1_id.user_id.id == current_user.id
            )
            rec.can_verified = can_approve

    @api.depends('state', 'approverhrd_id')
    def _compute_can_approve_hrd(self):
        """
        Button Approve (HR) muncul jika:
        1. State = verified
        2. Current user = approverhrd_id
        3. Field approverhrd_id ada isinya
        4. Sudah di approve oleh  'approval_l1_id', 'approval_l2_id'
        """
        current_user = self.env.user

        for rec in self:
            can_approve = (
                    rec.state == 'verified'
                    and rec.approval_l1_id
                    and rec.approve1
                    and rec.approval_l2_id
                    and rec.approve2
                    and rec.approverhrd_id.user_id.id == current_user.id
            )
            rec.can_approve_hrd = can_approve

    # Query Variables
    GET_APPROVER_QUERY = """
                         WITH
                             -- Ambil data employee utama + user
                             employee_base AS (SELECT he.id,
                                                      he.name,
                                                      he.user_id,
                                                      he.parent_id,
                                                      he.coach_id,
                                                      ru.login AS login,
                                                      ru.id    AS login_id
                                               FROM hr_employee he
                                                        LEFT JOIN res_users ru ON he.user_id = ru.id),
                             -- Ambil data parent (atasan langsung)
                             employee_parent AS (SELECT he2.id        AS parent_id,
                                                        he2.name      AS parent_name,
                                                        he2.parent_id AS parent_parent_id
                                                 FROM hr_employee he2),
                             -- Ambil data coach langsung (bisa dari coach_id)
                             employee_coach AS (SELECT he3.id   AS coach_id,
                                                       he3.name AS coach_name
                                                FROM hr_employee he3),
                             -- Ambil data coach parent (coach dari parent, jika diisi)
                             employee_coach_parent AS (SELECT he4.id   AS coach_parent_id,
                                                              he4.name AS coach_parent_name
                                                       FROM hr_employee he4)

                         SELECT eb.id                                                    AS employee_id,
                                eb.name                                                  AS employee,
                                eb.login,
                                eb.parent_id,
                                COALESCE(eb.coach_id, ep.parent_parent_id, eb.parent_id) AS coach_id,

                                -- Mencari nama coach/approver berdasarkan ID yang terpilih
                                CASE
                                    WHEN eb.coach_id IS NOT NULL
                                        THEN (SELECT name FROM hr_employee WHERE id = eb.coach_id)
                                    WHEN ep.parent_parent_id IS NOT NULL
                                        THEN (SELECT name FROM hr_employee WHERE id = ep.parent_parent_id)
                                    ELSE (SELECT name FROM hr_employee WHERE id = eb.parent_id)
                                    END                                                  AS coach_name

                         FROM employee_base eb
                                  LEFT JOIN employee_parent ep ON eb.parent_id = ep.parent_id

                         WHERE eb.id = %s; \
                         """

    # ========================================
    # Helper Method: Checking constrain request day payment at same day
    # ========================================

    @api.constrains('used_at', 'employee_id', 'day_payment')
    def _check_request_day_payment_same_day(self):
        """Mencegah pengajuan Day Payment lebih dari 1 kali pada hari yang sama untuk karyawan yang sama."""
        for record in self:
            if record.day_payment and record.used_at and record.employee_id:
                existing_requests = self.env['hr.overtime.planning'].search([
                    ('id', '!=', record.id),
                    ('employee_id', '=', record.employee_id.id),
                    ('day_payment', '=', True),
                    ('used_at', '=', record.used_at),
                    ('state', '!=', 'reject'),  # Abaikan yang sudah ditolak
                ])
                if existing_requests:
                    raise ValidationError(
                        _("Karyawan %s sudah memiliki pengajuan Day Payment pada tanggal %s. "
                          "Tidak diperbolehkan mengajukan lebih dari satu kali pada hari yang sama.")
                        % (record.employee_id.name, record.used_at)
                    )

    # ========================================
    # Helper Method: Execute Query Above
    # ========================================
    def _execute_approver_query(self, employee_id):
        """
        Execute approver query dan return hasil

        Args:
            employee_id: ID dari employee

        Returns:
            dict: Result dari query atau False jika tidak ada data
        """
        if not employee_id:
            return False

        self.env.cr.execute(self.GET_APPROVER_QUERY, (employee_id,))
        result = self.env.cr.dictfetchall()

        return result[0] if result else False

    @api.depends('employee_id')
    def _get_approver_l1_l2(self):
        """
        Mendapatkan kedua Approver Level 1 & 2 sekaligus
        """
        for rec in self:
            rec.approval_l1_id = False
            rec.approval_l2_id = False

            if not rec.employee_id:
                continue

            employee_id = rec.employee_id.id
            result = rec._execute_approver_query(employee_id)

            if result:
                if result.get('parent_id'):
                    rec.approval_l1_id = result['parent_id']
                if result.get('coach_id'):
                    rec.approval_l2_id = result['coach_id']

    @api.onchange('periode_id')
    def _onchange_periode_id(self):
        """Update area_id and branch_id based on periode_id and apply dynamic domain."""
        if self.periode_id:
            self.area_id = self.periode_id.area_id.id if self.periode_id.area_id else False
            self.branch_id = self.periode_id.branch_id.id if self.periode_id.branch_id else False
        else:
            self.area_id = False
            self.branch_id = False
            return {
                'domain': {
                    'area_id': [],
                    'branch_id': [],
                }
            }

    def _reset_sequence_overtime_employees(self):
        """ restart running number """
        sequences = self.env['ir.sequence'].search(
            [('code', '=like', '%hr.overtime.planning%')])
        sequences.write({'number_next_actual': 1})

    """
    Button approval, sebisa mungkin digunakan hanya untuk mengubah state atau memberi nilai kepada field.
    Hindari menggunakan button approval untuk:
        1. Validasi -> lebih baik gunakan SQL constrains atau Python constrains
        2. Valuasi -> buat di private method terpisah, 1 method hanya boleh mengerjakan 1 task
    
    Approval sangat penting, maka, kode harus sesedikit mungkin untuk 
    meningkatkan readability sehingga mudah dipahami ketika debugging
    """

    def btn_approved_l1(self):
        """
        Aksi untuk menyetujui permintaan lembur pada Level 1 (approve1).
        Melakukan validasi dan pembaruan data terkait lembur (OT).
        DITAMBAHAKAN PRINT UNTUK DEBUGGING LOGIKA PENGURANGAN (Day Payment).
        """
        for record in self:
            if not record.hr_ot_planning_ids:
                raise UserError(
                    "Tidak dapat menyetujui permintaan lembur tanpa data karyawan.")
            if record.day_payment and record.total_hours < 7:
                raise UserError(
                    "Day Payment hanya bisa di-approve apabila total jam = 7 jam")
            if record.hr_ot_planning_ids:
                remaining_hours_for_deduction = 7

                for line in record.hr_ot_planning_ids:
                    if not record.day_payment:
                        if not line.ot_type:
                            raise UserError(
                                "Tidak dapat menyetujui permintaan lembur jika Jenis OT (Type OT) kosong.")
                        if not line.work_plann or not line.output_plann:
                            raise UserError(
                                "Tidak dapat menyetujui permintaan lembur jika Rencana Kerja atau Perkiraan Hasil kosong.")
                        if not line.plann_date_from:
                            raise UserError(
                                "Tidak dapat menyetujui permintaan lembur jika Rencana Tgl OT kosong.")
                    else:
                        if remaining_hours_for_deduction > 0 and line.is_select:
                            residual_ot_value = line.residual_ot
                            ot_to_deduct_on_line = 0
                            if residual_ot_value >= remaining_hours_for_deduction:
                                ot_to_deduct_on_line = remaining_hours_for_deduction
                                line.residual_ot -= ot_to_deduct_on_line
                                line.spl_employee_id.residual_ot -= ot_to_deduct_on_line
                                remaining_hours_for_deduction = 0
                            elif remaining_hours_for_deduction > residual_ot_value:
                                ot_to_deduct_on_line = residual_ot_value
                                line.residual_ot = 0
                                line.spl_employee_id.residual_ot = 0
                                remaining_hours_for_deduction -= ot_to_deduct_on_line
                        if not line.is_select:
                            line.unlink()
            record.write({
                'approve1': True,
                'state': 'approved_l1'
            })

    def btn_approved_l2(self):
        for rec in self:
            if not rec.day_payment:
                if not rec.hr_ot_planning_ids:
                    raise UserError(
                        "Tidak dapat menyetujui permintaan lembur tanpa data karyawan.")
                if rec.hr_ot_planning_ids:
                    for line in rec.hr_ot_planning_ids:
                        if not rec.day_payment:
                            if not line.ot_type:
                                raise UserError(
                                    "Tidak dapat menyetujui permintaan lembur jika Type OT kosong.")
                            if not line.work_plann or not line.output_plann:
                                raise UserError(
                                    "Tidak dapat menyetujui permintaan lembur jika rencana kerja kosong atau perkiraan hasil.")
                            if not line.plann_date_from:
                                raise UserError(
                                    "Tidak dapat menyetujui permintaan lembur jika rencana tgl OT kosong.")
            rec.approve2 = True
            rec.state = 'approved_l2'

    def btn_verified(self):
        for rec in self:
            for line in rec.hr_ot_planning_ids:

                if not line.day_payment:
                    line.residual_ot = line.adv_total_ot
                    if not line.verify_time_from or not line.verify_time_to:
                        raise UserError(
                            "Jam Verifikasi dari dan hingga harus diisi sebelum memverifikasi.")
                    if not line.output_realization:
                        raise UserError(
                            "Hasil Realisasi, kosong. Mohon diisi sebelum memverifikasi.")
                # if not line.realization_date or not line.realization_time_from or not line.realization_time_to:
                #     raise UserError(
                #         "Jam dan tanggal Realisasi dari dan hingga harus diisi.")
            rec.state = 'verified'

    def btn_approved(self):
        for rec in self:
            rec.state = 'approved'
            rec.approve3 = True

    def btn_done(self):
        for rec in self:
            rec.state = 'done'

    def btn_complete(self):
        for rec in self:
            rec.state = 'complete'

    def btn_reject(self):
        for rec in self:
            rec.state = 'reject'
            if rec.day_payment:
                for line in rec.hr_ot_planning_ids:
                    line.residual_ot = line.adv_total_ot
                    line.spl_employee_id.residual_ot = line.adv_total_ot

    def btn_backdraft(self):
        for rec in self:
            rec.state = 'draft'
            rec.approve1 = False
            rec.approve2 = False
            rec.approve3 = False
            if rec.day_payment:
                for line in rec.hr_ot_planning_ids:
                    line.residual_ot = line.adv_total_ot
                    line.spl_employee_id.residual_ot = line.adv_total_ot

    def btn_print_pdf(self):
        return self.env.ref('sanbe_hr_tms.overtime_request_report').report_action(self)

    def action_generate_ot(self):
        try:
            self.env.cr.execute("CALL generate_ot_request()")
            self.env.cr.commit()
            _logger.info("Stored procedure executed successfully.")
        except Exception as e:
            _logger.error("Error calling stored procedure: %s", str(e))
            raise UserError("Error executing the function: %s" % str(e))

    @api.depends('request_date', 'hrms_department_id', 'division_id')
    def _compute_req_day_name(self):
        for record in self:
            if record.request_date and record.hrms_department_id and record.division_id:
                day_name = record.request_date.strftime('%A')
                tgl = record.request_date.strftime('%y/%m/%d')
                record.request_day_name = f"{tgl} - {day_name}"
            else:
                record.request_day_name = False

    @api.depends('hr_ot_planning_ids')
    def _compute_record_employees(self):
        for record in self:
            record.count_record_employees = len(record.hr_ot_planning_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                branch_id = vals.get('branch_id')
                area_id = vals.get('area_id')
                # Fetch area and branch if missing
                if not area_id or not branch_id:
                    periode_id = vals.get('periode_id')
                    if periode_id:
                        periode = self.env['hr.opening.closing'].sudo().search(
                            [('id', '=', int(periode_id))], limit=1)
                        if periode:
                            branch_id = periode.branch_id.id
                            vals['area_id'] = periode.area_id.id
                            vals['branch_id'] = branch_id
                hrms_department_id = vals.get('hrms_department_id')
                department = self.env['sanhrms.department'].sudo().search([('id', '=', int(hrms_department_id))],
                                                                          limit=1)
                branch = self.env['res.branch'].sudo().search(
                    [('id', '=', int(branch_id))], limit=1)
                if department and branch:
                    department_code = department.department_code
                    branch_unit_id = branch.unit_id
                    tgl = fields.Date.today()
                    tahun = str(tgl.year)[2:]
                    bulan = str(tgl.month)
                    if vals['day_payment'] != True:
                        sequence_code = self.env['ir.sequence'].next_by_code(
                            'hr.overtime.planning')
                        vals['name'] = f"{tahun}/{bulan}/{branch_unit_id}/RA/{department_code}/{sequence_code}"
                    else:
                        sequence_code = self.env['ir.sequence'].next_by_code(
                            'hr.overtime.planning.dp')
                        vals['name'] = f"{tahun}/{bulan}/{branch_unit_id}/DP/{department_code}/{sequence_code}"
        return super(HREmpOvertimeRequest, self).create(vals_list)

    def unlink(self):
        for record in self:
            """Check if there are any detail records linked to this master record"""
            if record.hr_ot_planning_ids and record.state != 'draft':
                raise ValidationError(
                    _("You cannot delete this record as it has related detail records.")
                )
        return super().unlink()

    # ================================================================================
    # Helper Method: Get data from OT detail to day payment detail
    # ================================================================================

    def _compute_ot_detail_lines(self):
        for dp in self:
            line_commands = [(5, 0, 0)]
            if not dp.day_payment and dp.employee_id:
                line_commands.append((0, 0, {
                    'planning_id': dp.id,
                    'branch_id': dp.branch_id.id,
                    'area_id': dp.area_id.id,
                    'department_id': dp.department_id.id,
                    'employee_id': dp.employee_id.id,
                    'directorate_id': dp.directorate_id.id,
                    'hrms_department_id': dp.hrms_department_id.id,
                    'division_id': dp.division_id.id,
                    'plann_date_from': dp.periode_from,
                    'plann_date_to': dp.periode_from,
                    'ot_type': 'regular',
                    'is_select': False,
                }))
            elif dp.day_payment and dp.employee_id:

                ot_details = self.env['hr.overtime.employees'].search([
                    ('planning_id.employee_id', '=', dp.employee_id.id),
                    ('planning_id.day_payment', '=', False),
                    ('realization_date', '!=', False),
                    ('residual_ot', '>', 0),
                    ('state', 'in', ('verified', 'approved', 'complete', 'done')),
                ])

                for ot in ot_details:
                    spl_employee_id = ot.id
                    line_commands.append((0, 0, {
                        'planning_id': dp.id,
                        'branch_id': ot.branch_id.id,
                        'area_id': ot.area_id.id,
                        'department_id': ot.department_id.id,
                        'employee_id': ot.employee_id.id,
                        'directorate_id': ot.directorate_id.id,
                        'hrms_department_id': ot.hrms_department_id.id,
                        'division_id': ot.division_id.id,
                        'spl_employee_id': spl_employee_id,
                        'realization_date': ot.realization_date,
                        'realization_time_from': ot.realization_time_from,
                        'realization_time_to': ot.realization_time_to,
                        'plann_date_from': ot.plann_date_from,
                        'plann_date_to': ot.plann_date_to,
                        'ot_plann_from': ot.ot_plann_from,
                        'ot_plann_to': ot.ot_plann_to,
                        'verify_time_from': ot.verify_time_from,
                        'verify_time_to': ot.verify_time_to,
                        'work_plann': ot.work_plann,
                        'count_approval_ot': ot.count_approval_ot,
                        'claim_approval_ot': ot.claim_approval_ot,
                        'adv_total_ot': ot.adv_total_ot,
                        'sum_total_ot': ot.sum_total_ot,
                        'residual_ot': ot.residual_ot,
                        'output_plann': ot.output_plann,
                        'ot_type': 'dp',
                        'is_select': False,
                    }))

            dp.hr_ot_planning_ids = line_commands

    @api.onchange('employee_id')
    def get_ot_detail_to_dp_detail(self):
        self._compute_ot_detail_lines()

    # @api.depends('employee_id')
    # def _get_ot_detail_to_dp_detail(self):
    #     self._compute_ot_detail_lines()


class HREmpOvertimeRequestEmployee(models.Model):
    _name = "hr.overtime.employees"
    _description = 'HR Employee Overtime Planning Request Employee'

    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch',
                                  store=False)
    planning_id = fields.Many2one('hr.overtime.planning', string='HR Overtime Request Planning', cascade=True,
                                  index=True)
    periode_id = fields.Many2one('hr.opening.closing', string='Period', related='planning_id.periode_id', store=True,
                                 index=True)
    name = fields.Char(store=True, index=True,
                       compute="get_name", string="Name")

    @api.depends('planning_id', 'planning_id.employee_id', 'plann_date_from')
    def get_name(self):
        for line in self:
            employee_name = str(line.planning_id.employee_id.name or '')
            date_from = str(line.plann_date_from or '')

            if line.planning_id.day_payment:
                line.name = f"{employee_name} - DP - {date_from}"
            else:
                line.name = f"SPL {employee_name} - {date_from}"

    spl_employee_id = fields.Many2one(
        'hr.overtime.employees', string='SPL Employee Reference', index=True)
    areah_id = fields.Many2one('res.territory', string='Area ID Header', related='planning_id.area_id', index=True,
                               readonly=True)
    approverst_id = fields.Many2one('parent.hr.employee', related='employee_id.parent_id', string='Atasan Langsung',
                                    store=True, index=True)
    approvernd_id = fields.Many2one('parent.hr.employee', string='Atasan', compute='_get_approver', store=True,
                                    index=True)
    state = fields.Selection(
        related="planning_id.state", store=True, index=True)

    @api.depends('employee_id')
    def _get_approver(self):
        for rec in self:
            if rec.employee_id:
                emp = self.env['hr.employee'].sudo().search(
                    [('id', '=', rec.employee_id.id)], limit=1)
                if emp:
                    if emp.coach_id:
                        rec.approvernd_id = emp.coach_id.id
                    else:
                        rec.approvernd_id = self.env['hr.employee'].browse(
                            emp.parent_id.id).parent_id.id

    area_id = fields.Many2one(
        'res.territory', string='Area', related='planning_id.area_id', index=True)
    branch_id = fields.Many2one('res.branch', related='planning_id.branch_id',
                                string='Bisnis Unit Header', index=True, readonly=True)
    department_id = fields.Many2one(
        'hr.department', related='planning_id.department_id', domain="[('id','in',alldepartment)]",
        string='Sub Department')

    division_id = fields.Many2one(
        'sanhrms.division', string='Divisi', related='planning_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen',
                                         related='planning_id.hrms_department_id', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', related='planning_id.directorate_id',
                                     store=True)
    nik = fields.Char('NIK Karyawan', related='employee_id.nik',
                      index=True, store=True)
    employee_id = fields.Many2one('hr.employee', domain="[('state','=','approved')]", related='planning_id.employee_id',
                                  string='Nama Karyawan', index=True, store=True)
    max_hours_week = fields.Float(
        'Total Jam Week', related='employee_id.max_hours_week', digits=(200, 1), default=40, store=True)
    max_days_month = fields.Integer(
        'Total Hari Kerja Month', digits=(31, 1), related='employee_id.max_days_month', default=22, store=True)
    max_ot = fields.Float(
        'Max OT/Hari', related='employee_id.max_ot', digits=(16, 1), store=True)
    max_ot_month = fields.Float(
        'Jam Max OT/Bulan', related='employee_id.max_ot_month', store=True)
    periode_from = fields.Date('Tanggal OT Dari', related='planning_id.periode_from', store=True,
                               default=fields.Date.today)
    periode_to = fields.Date('Tanggal OT Hingga', related='planning_id.periode_to', store=True,
                             default=fields.Date.today)
    day_payment = fields.Boolean(
        'Day Payment', related='planning_id.day_payment', store=True)
    plann_date_from = fields.Date('Tanggal SPL')
    plann_date_to = fields.Date('Jam SPL Dari')
    ot_plann_from = fields.Float('Jam SPL dari', digits=(4, 1))
    ot_plann_to = fields.Float('Jam SPL Hingga', digits=(4, 1))
    approve_time_from = fields.Float('OT App From')
    approve_time_to = fields.Float('OT App To')
    realization_date = fields.Date('Realization Date')
    realization_time_from = fields.Float('Jam Hadir Dari')
    realization_time_to = fields.Float('Jam Hadir Hingga')
    verify_time_from = fields.Float('Verifkasi Jam Dari')
    verify_time_to = fields.Float('Verifkasi Jam Hingga')

    # def counting_hours(self, start, end):
    #     """Calculate the number of hours between two times, considering overnight shifts."""
    #     if end < start:
    #         end += 24.0  # Adjust for overnight shifts
    #     return end - start

    count_approval_ot = fields.Float('Total Jam Approval OT', store=True)
    claim_approval_ot = fields.Float('Total Jam yang di klaim OT', store=True)
    sum_total_ot = fields.Float('Jumlah Total OT', store=True)
    adv_total_ot = fields.Float('Kelebihan Jam Verifikasi OT', store=True)
    residual_ot = fields.Float(
        'Sisa Jam OT', store=True, help='Sisa jam lembur yang dapat dipilih untuk Day Payment')
    machine = fields.Char('Machine')
    work_plann = fields.Char('Rencana SPL')
    output_plann = fields.Char('Output SPL')
    output_realization = fields.Char('Hasil Realisasi')
    explanation_deviation = fields.Char('Explanation Deviation')
    branch_id = fields.Many2one('res.branch', related='planning_id.branch_id', domain="[('id','in',branch_ids)]",
                                string='Business Unit', index=True)
    department_id = fields.Many2one(
        'hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    bundling_ot = fields.Boolean(string="Bundling OT")
    transport = fields.Boolean('Transport')
    meals = fields.Boolean(string='Meal Dine In')
    meals_cash = fields.Boolean(string='Meal Cash')
    route_id = fields.Many2one(
        'sb.route.master', domain="[('branch_id','=',branch_id)]", string='Rute')
    ot_type = fields.Selection(
        [('regular', 'Regular'),  # Perhitungan Lembur hari kerja
         ('holiday', 'Holiday'),  # Perhitungan Lembur hari libur
         # Perhitungan lembur yang seluruh jam terverifikasinya dijadikan Day Payment
         ('dp', 'Day Payment')
         ], string='Tipe SPL')
    is_approval = fields.Selection([('approved', 'Approved'), ('reject', 'Tolak')], default='approved',
                                   string="Approval")
    is_approved_l2 = fields.Boolean('Approved by MGR', default=True)
    is_select = fields.Boolean('Select', default=False)

    planning_req_name = fields.Char(
        string='Planning Request Name', required=False)

    @api.depends('state', 'adv_total_ot')
    def assign_val_tor_resudual_ot(self):
        for rec in self:
            if rec.state == 'verified' and not rec.planning_id.day_payment:
                if not rec.residual_ot:
                    rec.residual_ot = rec.adv_total_ot

    @api.constrains('ot_plann_from', 'ot_plann_to', 'max_ot')
    def _check_time_range(self):
        """
        Check that the planned overtime hours are between 0.0 and 24.0
        and that the 'from' time is less than the 'to' time.
        """
        for record in self:
            if not record.ot_plann_from or not record.ot_plann_to:
                continue

            if not (0.0 <= record.ot_plann_from <= 24.0 and
                    0.0 <= record.ot_plann_to <= 24.0):
                raise UserError("Waktu harus dalam rentang 0.0 hingga 25.0.")
            # if record.ot_plann_from >= record.ot_plann_to:
            #     raise UserError(
            #         "Jam SPL 'dari' harus lebih awal dari jam SPL 'Hingga'.")
            # if record.max_ot and (record.ot_plann_to - record.ot_plann_from) > record.max_ot:
            #     raise UserError(
            #         "Jam SPL melebihi batas maksimal jam lembur karyawan.")

    @api.constrains('plann_date_from', 'periode_to', 'periode_from')
    def _check_validation_date(self):
        for line in self:
            if line.plann_date_from and line.periode_from and line.periode_to and \
                    (
                            line.plann_date_from < line.periode_from or line.plann_date_from > line.periode_to) and not line.day_payment:
                msg = "Tanggal SPL (%s) harus berada di antara Tanggal OT Dari (%s) dan Tanggal OT Hingga (%s)." % (
                    line.plann_date_from, line.periode_from, line.periode_to
                )
                raise UserError(msg)

    @api.model_create_multi
    def create(self, vals_list):
        records_vals = vals_list if isinstance(
            vals_list, list) else [vals_list]

        for vals in records_vals:
            ot_from = vals.get('ot_plann_from', 0.0)
            ot_to = vals.get('ot_plann_to', 0.0)
            plann_date = vals.get('plann_date_from')
            periode_from = vals.get('periode_from')
            periode_to = vals.get('periode_to')
            day_payment = vals.get('day_payment')
            if not (0.0 <= ot_from <= 24.0 and 0.0 <= ot_to <= 24.0):
                raise UserError("Waktu harus dalam rentang 0.0 hingga 24.0.")
            if plann_date and periode_from and periode_to and not day_payment:
                if plann_date < periode_from or plann_date > periode_to:
                    msg = "Tanggal SPL (%s) harus berada di antara Tanggal OT Dari (%s) dan Tanggal OT Hingga (%s)." % (
                        plann_date, periode_from, periode_to
                    )
                    raise UserError(msg)
        return super(HREmpOvertimeRequestEmployee, self).create(records_vals)

    @api.onchange('is_approval')
    def _ubah_approved_l2(self):
        for rec in self:
            if rec.is_approval == 'approved':
                rec.is_approved_l2 = True
            else:
                rec.is_approved_l2 = False

    def act_detail(self):
        for line in self:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Search Employee'),
                'res_model': 'hr.overtime.employees',
                'view_mode': 'form',
                'target': 'new',
                'res_id': line.id,
                'views': [[False, 'form']],
                'view_id': self.env.ref('sanbe_hr_tms.hr_overtime_employees_form').id,
            }
