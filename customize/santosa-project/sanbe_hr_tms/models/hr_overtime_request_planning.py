# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
from email.policy import default

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import pytz
from datetime import datetime,time, timedelta
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
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]
            
    @api.depends('area_id','branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            allbranch = self.env['hr.department'].sudo().search([('branch_id','=', allrecs.branch_id.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]

    def _get_running_periode(self):
        """Mendapatkan periode 'running' yang aktif untuk Branch pengguna saat ini."""
        user_branch_id = self.env.user.branch_id.id
        if not user_branch_id:
            return False

        return self.env['hr.opening.closing'].search([
            ('state_process', 'in', ('draft','running')),
            ('branch_id', '=', user_branch_id),
            ('open_periode_from', '<=', fields.Datetime.now()),
            ('open_periode_to', '>=', fields.Datetime.now())
        ], order='id desc', limit=1)

    name = fields.Char('Nomor Surat Perintah Lembur',default=lambda self: _('New'),
       copy=False, readonly=True, tracking=True, requirement=True)
    request_date = fields.Date('Tanggal Surat Perintah Lembur', default=fields.Date.today(), readonly=True)
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

    branch_id = fields.Many2one(
        'res.branch',
        string='Bisnis Unit',
        copy=True,
        index=True,
        # domain="[('id','in',self.env.user.branch_id.id)]",
        default=lambda self: self.env.user.branch_id.id,
        tracking=True
    )
    alldepartment = fields.Many2many('hr.department','hr_department_plan_ot_rel', string='All Department',compute='_isi_department_branch',store=False)
    department_id = fields.Many2one('hr.department',domain="[('id','in',alldepartment)]", string='Sub Department')
    division_id = fields.Many2one('sanhrms.division',string='Divisi', default=lambda self: self.env.user.employee_id.division_id.id , domain="[('hrms_department_id','=',hrms_department_id)]", store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', default=lambda self: self.env.user.employee_id.hrms_department_id.id, domain="[('directorate_id','=',directorate_id)]", store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', default=lambda self: self.env.user.employee_id.directorate_id.id, domain="['|',('branch_id','=',branch_id),('branch_id','=',False)]", store=True)
    employee_id = fields.Many2one('hr.employee','nama Karyawan', domain="[('state','=','approved'),('division_id','=',division_id),'|',('branch_id','=',branch_id),('branch_id','=',False)]", store=True)
    periode_from = fields.Date('Perintah Lembur Dari',default=fields.Date.today)
    periode_to = fields.Date('Hingga',default=fields.Date.today)
    approve1 = fields.Boolean('Approval L1',default=False)
    approve2 = fields.Boolean('Approval L2',default=False)
    approve3 = fields.Boolean('Approval by HCM',default=False)
    state = fields.Selection(
        selection=TMS_OVERTIME_STATE,
        string="TMS Overtime Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft')
    periode_id = fields.Many2one('hr.opening.closing',string='Period',domain="[('branch_id','=',branch_id),('state','in',('draft','running'))]", index=True, default=_get_running_periode)
    hr_ot_planning_ids = fields.One2many('hr.overtime.employees','planning_id', auto_join=True, index=True, required=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan',)
    company_id = fields.Many2one('res.company', string="Company Name", index=True)
    request_day_name = fields.Char('Request Day Name', compute='_compute_req_day_name', store=True)
    count_record_employees = fields.Integer(string="Total Employees on The List", compute="_compute_record_employees", store=True)
    approverst_id = fields.Many2one('parent.hr.employee', related = 'employee_id.parent_id', string='Atasan Langsung',store=True, index=True)
    approvernd_id = fields.Many2one('parent.hr.employee', string='Atasan', compute = '_get_approver',store=True ,index=True)
    approverhrd_id = fields.Many2one('hr.employee', string='Atasan', domain="[('hrms_department_id', 'in', (97, 174))]", store=True, index=True)

    # New fields for user_id
    approverst_user_id = fields.Many2one('res.users', related='approverst_id.user_id', string='User for Atasan Langsung', store=True)
    approvernd_user_id = fields.Many2one('res.users', related='approvernd_id.user_id', string='User for Atasan', store=True)
    approverhrd_user_id = fields.Many2one('res.users', related='approverhrd_id.user_id', string='User for HRD', store=True)

    @api.depends('employee_id')
    def _get_approver(self):
        for rec in self:
            if rec.employee_id:
                emp = self.env['hr.employee'].sudo().search([('id','=',rec.employee_id.id)],limit=1)
                emp_1 = self.env['hr.employee'].browse(emp.parent_id.id).parent_id.id
                if emp:
                    if emp.coach_id:
                        rec.approvernd_id = emp.coach_id.id
                    elif emp_1:
                        rec.approvernd_id = emp_1
                    elif not emp_1:
                        rec.approvernd_id = rec.employee_id.parent_id.id

    show_approval_l1_button = fields.Boolean(compute='_compute_show_approval_buttons',store=False, default=False)
    show_approval_l2_button = fields.Boolean(compute='_compute_show_approval_buttons',store=False, default=False)
    show_approval_button = fields.Boolean(compute='_compute_show_approval_buttons',store=False, default=False)

    @api.depends('state', 'approverst_id.user_id', 'approvernd_id.user_id', 'approverhrd_id')
    def _compute_show_approval_buttons(self):
        user = self.env.user
        admin_user = self.env.ref('base.user_root')
        current_employee = user.employee_id
        current_employee_id = current_employee.id if current_employee else False
        for rec in self:
            rec.show_approval_l1_button = False
            rec.show_approval_l2_button = False
            rec.show_approval_button = False
            if not rec.approverst_user_id :
                rec.show_approval_l1_button = False
            if not rec.approvernd_user_id :
                rec.show_approval_l2_button = False
            if not rec.approverhrd_user_id:
                rec.show_approval_button = False
            approverst_employee_id = rec.approverst_id.id
            approvernd_employee_id = rec.approvernd_id.id
            approverhrd_employee_id = rec.approverhrd_id.id
            has_supervisor_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_supervisor')
            has_namager_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_manager')
            is_approver_st = (current_employee_id and current_employee_id == approverst_employee_id)
            if has_namager_group or has_supervisor_group:
                if rec.state == 'draft' and has_supervisor_group:
                    if user == admin_user or is_approver_st:
                        rec.show_approval_l1_button = True
                if rec.state == 'approved_l2' and has_supervisor_group:
                    if user.id == admin_user.id or is_approver_st:
                        rec.show_approval_l1_button = True
                if rec.state == 'approved_l1' and has_supervisor_group:
                    is_approver_nd = (current_employee_id and current_employee_id == approvernd_employee_id)
                    if user.id == admin_user.id or is_approver_nd:
                        rec.show_approval_l2_button = True
                if rec.state == 'verified' and has_supervisor_group:
                    is_approver_hrd = (current_employee_id and current_employee_id == approverhrd_employee_id)
                    if user.id == admin_user.id:
                        rec.show_approval_button = True
                    elif is_approver_hrd:
                        rec.show_approval_button = True
                    else:
                        rec.show_approval_button = True

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

    # restart running number
    def _reset_sequence_overtime_employees(self):
        sequences = self.env['ir.sequence'].search([('code', '=like', '%hr.overtime.planning%')])
        sequences.write({'number_next_actual': 1})

    def unlink(self):
        for record in self:
            # Check if there are any detail records linked to this master record
            if record.hr_ot_planning_ids and record.state != 'draft':
                raise ValidationError(
                    _("You cannot delete this record as it has related detail records.")
                )
        return super().unlink()

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
                        periode = self.env['hr.opening.closing'].sudo().search([('id', '=', int(periode_id))], limit=1)
                        if periode:
                            branch_id = periode.branch_id.id
                            vals['area_id'] = periode.area_id.id
                            vals['branch_id'] = branch_id
                hrms_department_id = vals.get('hrms_department_id')
                department = self.env['sanhrms.department'].sudo().search([('id', '=', int(hrms_department_id))], limit=1)
                branch = self.env['res.branch'].sudo().search([('id', '=', int(branch_id))], limit=1)
                if department and branch:
                    department_code = department.department_code
                    branch_unit_id = branch.unit_id
                    tgl = fields.Date.today()
                    tahun = str(tgl.year)[2:]
                    bulan = str(tgl.month)
                    sequence_code = self.env['ir.sequence'].next_by_code('hr.overtime.planning')
                    vals['name'] = f"{tahun}/{bulan}/{branch_unit_id}/RA/{department_code}/{sequence_code}"
        return super(HREmpOvertimeRequest, self).create(vals_list)
    
    def btn_approved(self):
        user = self.env.user
        admin_user = self.env.ref('base.user_root')
        self_employee = self.env.user.employee_id.id
        is_rd_approver = self_employee == self.approverhrd_id.id
        has_supervisor_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_supervisor')
        has_namager_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_manager')
        for rec in self:
            if rec.approve1 == True and rec.approve2 == True:
                if has_namager_group:
                    # is_rd_approver = True
                    if is_rd_approver or admin_user:
                        rec.state = 'approved'
                        rec.approve3 = True
                elif has_supervisor_group:
                    if is_rd_approver or admin_user:
                        rec.state = 'approved'
                        rec.approve3 = True
                else:
                    raise UserError('You are not authorized to approve this request.')
            else:
                raise UserError('Approve Not Complete')
    
    def btn_done(self):
        for rec in self:
            rec.state = 'done'

    # @api.model
    # def _get_visible_states(self):
    #     """Menentukan state mana yang akan ditampilkan berdasarkan state saat ini"""
    #     self.ensure_one()
    #     if self.state == '':
    #         return 'draft,approved_mgr,done,reject'
    #     elif self.state == 'draft':
    #         return 'draft,approved_mgr,done,reject'
    #     elif self.state == 'approved_mgr':
    #         return 'draft,approved_mgr,done,reject'
    #     elif self.state == 'approved_pmr':
    #         return 'draft,approved_pmr,done,reject'
    #     elif self.state == 'approved':
    #         return 'draft,approved,done,reject'
    #     elif self.state == 'done':
    #         return 'draft,done,reject'
    #     elif self.state == 'reject':
    #         return 'draft,done,reject'
    #     else:
    #         return 'draft,approved_mgr,approved_pmr,approved,done,reject'

    def btn_approved_l2(self):
        user = self.env.user
        admin_user = self.env.ref('base.user_root')
        self_employee = self.env.user.employee_id.id
        is_nd_approver = self_employee == self.approvernd_id.id
        has_supervisor_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_supervisor')
        has_namager_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_manager')
        for rec in self:
            if has_supervisor_group or has_namager_group:
                if is_nd_approver  or admin_user:
                    rec.approve2 = True
                    rec.state = 'approved_l2'
                    rec.show_approval_l2_button = False 
            else:
                raise UserError('You are not authorized to approve this request.')
    def btn_complete(self):
        for rec in self:
            rec.state = 'complete'
            rec.state = 'done'


    def btn_verified(self):
        user = self.env.user
        admin_user = self.env.ref('base.user_root')
        self_employee = self.env.user.employee_id.id
        is_st_approver = self_employee == self.approverst_id.id
        has_supervisor_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_supervisor')
        has_namager_group = user.has_group('sanbe_hr_tms.module_role_overtime_request_manager')
        for rec in self:
            if len(rec.hr_ot_planning_ids) == 0:
                raise UserError('Tidak dapat memverifikasi permintaan lembur tanpa rincian karyawan.')
            if has_supervisor_group or has_namager_group:
                for line in rec.hr_ot_planning_ids:
                    if not line.verify_time_from or not line.verify_time_to:   
                        raise UserError('Tidak dapat memverifikasi permintaan lembur dengan rincian karyawan yang belum diverifikasi waktu lemburnya.') 
                if is_st_approver or admin_user:
                    rec.state = 'verified'
                    for line in rec.hr_ot_planning_ids:
                        if line.is_approval == 'reject':
                            line.unlink()

    def btn_approved_l1(self):
        admin_user = self.env.ref('base.user_root')
        self_employee = self.env.user.employee_id.id
        is_st_approver = self_employee == self.approverst_id.id
        for rec in self:
            if len(rec.hr_ot_planning_ids) == 0:
                raise UserError('Tidak dapat memverifikasi permintaan lembur tanpa rincian karyawan.')
            for line in rec.hr_ot_planning_ids:
                    if not line.output_plann or not line.verify_time_to:   
                        raise UserError('Tidak dapat memproses permintaan lembur dengan tanpa rencana lembur.') 
            if len(rec.hr_ot_planning_ids) == 0:
                raise UserError('Tidak dapat memproses permintaan lembur tanpa rincian karyawan.')
            if is_st_approver or admin_user:
                rec.approve1 = True
                rec.state = 'approved_l1'
                rec.show_approval_l1_button = False
            else:
                raise UserError('You are not authorized to approve this request.')
    
    def btn_reject(self):
        for rec in self:
            rec.state = 'reject'
    
    def btn_backdraft(self):
        for rec in self:
            rec.state = 'draft'

    def btn_print_pdf(self):
        return self.env.ref('sanbe_hr_tms.overtime_request_report').report_action(self)        

    # def action_search_employee(self):
    #     wizard = self.env['hr.employeedepartment'].create({
    #                 'plan_id': self.id,
    #                 'modelname':'hr.overtime.planning',
    #                 'area_id':self.area_id.id,
    #                 'branch_id':self.branch_id.id,
    #                 'department_id':self.department_id.id,
    #                 'division_id':self.division_id.id,
    #                 'hrms_department_id':self.hrms_department_id.id,
    #                 'directorate_id':self.directorate_id.id,
    #                 })
    #     emp_line = self.env['hr.employeedepartment.details'].search([('cari_id','=',wizard.id)])
    #     if not emp_line:
    #         wizard._isi_employee()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Search Employee'),
    #         'res_model': 'hr.employeedepartment',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'res_id': wizard.id,
    #         'domain': [('division_id', '=', self.division_id.id),('hrms_department_id', '=', self.hrms_department_id.id),('directorate_id', '=', self.directorate_id.id)],
    #         'views': [[False, 'form']]
        # }

    def action_generate_ot(self):
        try:
            self.env.cr.execute("CALL generate_ot_request()")
            self.env.cr.commit()
            _logger.info("Stored procedure executed successfully.")
        except Exception as e:
            _logger.error("Error calling stored procedure: %s", str(e))
            raise UserError("Error executing the function: %s" % str(e))

    @api.depends('request_date','hrms_department_id','division_id')
    def _compute_req_day_name(self):
        for record in self:
            if record.request_date and record.hrms_department_id and record.division_id   :
                day_name = record.request_date.strftime('%A')
                tgl = record.request_date.strftime('%y/%m/%d')
                record.request_day_name = f"{tgl} - {day_name}"
            else:
                record.request_day_name = False

    # def unlink(self):
    #     for record in self:
    #         if record.hr_ot_planning_ids:
    #             record.hr_ot_planning_ids.unlink()
    #     return super().unlink()

    @api.depends('hr_ot_planning_ids')
    def _compute_record_employees(self):
        for record in self:
            record.count_record_employees = len(record.hr_ot_planning_ids)   

class HREmpOvertimeRequestEmployee(models.Model):
    _name = "hr.overtime.employees"
    _description = 'HR Employee Overtime Planning Request Employee'

    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch',
                                  store=False)
    planning_id = fields.Many2one('hr.overtime.planning',string='HR Overtime Request Planning', cascade=True, index=True)
    areah_id = fields.Many2one('res.territory', string='Area ID Header', related='planning_id.area_id', index=True, readonly=True)
    approverst_id = fields.Many2one('parent.hr.employee', related = 'employee_id.parent_id', string='Atasan Langsung',store=True, index=True)
    approvernd_id = fields.Many2one('parent.hr.employee', string='Atasan', compute = '_get_approver',store=True ,index=True)
    state = fields.Selection(related="planning_id.state")

    @api.depends('employee_id')
    def _get_approver(self):
        for rec in self:
            if rec.employee_id:
                emp = self.env['hr.employee'].sudo().search([('id','=',rec.employee_id.id)],limit=1)
                if emp:
                    if emp.coach_id:
                        rec.approvernd_id = emp.coach_id.id
                    else:
                        rec.approvernd_id = self.env['hr.employee'].browse(emp.parent_id.id).parent_id.id

    area_id = fields.Many2one('res.territory', string='Area',index=True)
    branchh_id = fields.Many2one('res.branch', related='planning_id.branch_id', string='Bisnis Unit Header', index=True, readonly=True)
    departmenth_id = fields.Many2one('hr.department', related='planning_id.department_id',string='Department ID Header', index=True, readonly=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='planning_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', related='planning_id.hrms_department_id',store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='planning_id.directorate_id',store=True)
    nik = fields.Char('NIK Karyawan',related='employee_id.nik', index=True, store=True)
    # employee_ids = fields.Many2many('hr.employee','ov_plan_emp_rel', string='Employee Name',store=False)
    employee_id = fields.Many2one('hr.employee', domain="[('state','=','approved')]", related='planning_id.employee_id', string='Nama Karyawan',index=True)
    max_ot = fields.Float('Jam Lembur Maksimal', related='employee_id.max_ot', digits=(16, 1), default=0, store=True)
    max_ot_month = fields.Float('Jam Lembur Maksimal',  related='employee_id.max_ot_month', store=True)
    periode_from = fields.Date('Tanggal OT Dari', related='planning_id.periode_from', store=True, default=fields.Date.today)
    periode_to = fields.Date('Tanggal OT Hingga', related='planning_id.periode_to', store=True, default=fields.Date.today)
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
    machine = fields.Char('Machine')
    work_plann = fields.Char('Rencana SPL')
    output_plann = fields.Char('Output SPL')
    output_realization = fields.Char('Hasil Realisasi')
    explanation_deviation = fields.Char('Explanation Deviation')
    branch_id = fields.Many2one('res.branch', related='planning_id.branch_id', domain="[('id','in',branch_ids)]", string='Business Unit', index=True)
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    bundling_ot = fields.Boolean(string="Bundling OT")
    transport = fields.Boolean('Transport')
    meals = fields.Boolean(string='Meal Dine In')
    meals_cash = fields.Boolean(string='Meal Cash')
    route_id = fields.Many2one('sb.route.master', domain="[('branch_id','=',branch_id)]", string='Rute')
    ot_type = fields.Selection([('regular','Regular'),('holiday','Holiday')],string='Tipe SPL')
    is_approval = fields.Selection([('approved','Approved'),('reject','Tolak')], default='approved',string="Approval")
    is_approved_l2 = fields.Boolean('Approved by MGR',default=True)
    is_reject_mgr = fields.Boolean('Tolak',compute='rubah_approved_l2',default=False, store=True)
    planning_req_name = fields.Char(string='Planning Request Name',required=False)
    # _sql_constraints = [
    #     ('unique_employee_planning', 'unique(employee_id, planning_id)',
    #      'An employee cannot have duplicate overtime planning within the same date range and planning request.'),
    # ]

    @api.constrains('ot_plann_from', 'ot_plann_to','max_ot')
    def _check_time_range(self):
        """
        Check that the planned overtime hours are between 0.0 and 24.0
        and that the 'from' time is less than the 'to' time.
        """
        for record in self:
            if not (0.0 <= record.ot_plann_from <= 24.0 and 
                    0.0 <= record.ot_plann_to <= 24.0):
                raise UserError("Waktu harus dalam rentang 0.0 hingga 24.0.")
            if record.ot_plann_from >= record.ot_plann_to:
                raise UserError("Jam SPL 'dari' harus lebih awal dari jam SPL 'Hingga'.")
            if record.max_ot and (record.ot_plann_to - record.ot_plann_from) > record.max_ot:
                raise UserError("Jam SPL melebihi batas maksimal jam lembur karyawan.")

    @api.constrains('plann_date_from', 'periode_to', 'periode_from')
    def _check_validation_date(self):
        for line in self:
            if line.plann_date_from and line.periode_from and line.periode_to and \
               (line.plann_date_from < line.periode_from or line.plann_date_from > line.periode_to):
                msg = "Tanggal SPL (%s) harus berada di antara Tanggal OT Dari (%s) dan Tanggal OT Hingga (%s)." % (
                    line.plann_date_from, line.periode_from, line.periode_to
                )
                raise UserError(msg)
                
    @api.model_create_multi
    def create(self, vals_list):
        records_vals = vals_list if isinstance(vals_list, list) else [vals_list]

        for vals in records_vals:
            ot_from = vals.get('ot_plann_from', 0.0)
            ot_to = vals.get('ot_plann_to', 0.0)
            plann_date = vals.get('plann_date_from')
            periode_from = vals.get('periode_from')
            periode_to = vals.get('periode_to')

            # === Validation 1: Time Range ===
            if not (0.0 <= ot_from <= 24.0 and 0.0 <= ot_to <= 24.0):
                raise UserError("Waktu harus dalam rentang 0.0 hingga 24.0.")
            if ot_from >= ot_to:
                raise UserError("Jam SPL 'dari' harus lebih awal dari jam SPL 'Hingga'.")

            # === Validation 2: Date Range ===
            if plann_date and periode_from and periode_to:
                if plann_date < periode_from or plann_date > periode_to:
                    msg = "Tanggal SPL (%s) harus berada di antara Tanggal OT Dari (%s) dan Tanggal OT Hingga (%s)." % (
                        plann_date, periode_from, periode_to
                    )
                    raise UserError(msg)

        # ✅ Correct super() call
        return super(HREmpOvertimeRequestEmployee, self).create(records_vals)

    @api.constrains('plann_date_from')
    def _check_validation_date(self):
        for line in self:
            if line.plann_date_from > line.planning_id.periode_to and line.plann_date_from < line.planning_id.periode_from:
                raise UserError (('Date Must in between %s and %s')%(line.planning_id.periode_from,line.planning_id.periode_to))

    @api.onchange('is_approval')
    def _ubah_approved_l2(self):
        for rec in self:
            if rec.is_approval=='approved':
                rec.is_approved_l2 = True
                rec.is_reject_mgr = False
            else:
                rec.is_reject_mgr = True
                rec.is_approved_l2 = False

    def act_detail(self):
        for line in self:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Search Employee'),
                'res_model': 'hr.overtime.employees',
                'res_model': 'hr.overtime.employees',
                'view_mode': 'form',
                'target': 'new',
                'res_id': line.id,
                'views': [[False, 'form']],
                'view_id': self.env.ref('sanbe_hr_tms.hr_overtime_employees_form').id,
            }

    # @api.onchange('employee_id')
    # def rubah_employee(self):
    #     for rec in self:
    #         if rec.employee_id:
    #             emp = self.env['hr.employee'].sudo().search([('id','=',rec.employee_id.id)],limit=1)
    #             if emp:
    #                 rec.nik = emp.nik
                    #rec.branch_id = emp.branch_id.id
                    #rec.department_id = emp.department_id.id
                    #rec.area_id = emp.area.id
    #
    # @api.constrains('nik','plann_date_from','plann_date_to')
    # def check_duplicate_record(self):
    #     pass
    #     for rec in self:
    #         '''Method to avoid duplicate overtime request'''
    #         duplicate_record = self.search([
    #             ('nik','=',rec.nik),
    #             ('plann_date_from','=',rec.plann_date_from),
    #             ('plann_date_to','=',rec.plann_date_to),
    #         ])
    #         if duplicate_record:
    #             raise ValidationError(f"Duplicate record found for employee {rec.employee_id.name} in {rec.planning_id.name}. "
    #                                   f"Start date: {rec.plann_date_from} and end date: {rec.plann_date_to}.")
    #
    # @api.model
    # def create(self, vals):
    #     # Add the duplicate check before creating a new record
    #     # self.check_duplicate_record()
    #     return super(HREmpOvertimeRequestEmployee, self).create(vals)
    #
    # def write(self, vals):
    #     # Add the duplicate check before updating a record
    #     res = super(HREmpOvertimeRequestEmployee, self).write(vals)
    #     # self.check_duplicate_record()
    #     return res