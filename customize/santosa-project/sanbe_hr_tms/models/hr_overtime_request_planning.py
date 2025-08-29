# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import pytz
from datetime import datetime,time, timedelta
import logging
_logger = logging.getLogger(__name__)

TMS_OVERTIME_STATE = [
    ('draft', 'Draft'),
    ('approved_mgr', "Approved By MGR"),
    ('approved_pmr', "Approved By PMR"),
    ('approved', 'Approved By HCM'),
    ('done', "Close"),
    ('reject', "Reject"),
]
class HREmpOvertimeRequest(models.Model):
    _name = "hr.overtime.planning"
    _description = 'HR Employee Overtime Planning Request'
    _rec_name = 'name'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def _get_active_periode_from(self):
        mycari = self.env['hr.opening.closing'].sudo().search([('isopen','=',True)],limit=1)
        return mycari.open_periode_from or False

    def _get_active_periode_to(self):
        mycari = self.env['hr.opening.closing'].sudo().search([('isopen','=',True)],limit=1)
        return mycari.open_periode_to or False

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

    name = fields.Char('Planning Request',default=lambda self: _('New'),
       copy=False, readonly=True, tracking=True, requirement=True)
    request_date = fields.Date('Planning Request Create', default=fields.Date.today(), readonly=True)
    area_id = fields.Many2one(
        "res.territory",
        string='Area ID',
        copy=True,
        index=True,
        default=lambda self: self.env.user.area.id,
        required=True,
        tracking=True
    )
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)

    branch_id = fields.Many2one(
        'res.branch',
        string='Bisnis Unit',
        copy=True,
        index=True,
        # domain="[('id','in',branch_ids)]",
        default=lambda self: self.env.user.branch_id.id,
        tracking=True
    )
    alldepartment = fields.Many2many('hr.department','hr_department_plan_ot_rel', string='All Department',compute='_isi_department_branch',store=False)
    department_id = fields.Many2one('hr.department',domain="[('id','in',alldepartment)]",string='Sub Department')
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', store=True)
    periode_from = fields.Date('Period From',default=_get_active_periode_from)
    periode_to = fields.Date('Period To',default=_get_active_periode_to)
    approve1 = fields.Boolean('Supervisor Department',default=False)
    approve2 = fields.Boolean('Manager Department',default=False)
    approve3 = fields.Boolean('HCM Department',default=False)
    state = fields.Selection(
        selection=TMS_OVERTIME_STATE,
        string="TMS Overtime Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    periode_id = fields.Many2one('hr.opening.closing',string='Period',domain="[('branch_id','=',branch_id),('state','=','approved')]", index=True, required=True)
    hr_ot_planning_ids = fields.One2many('hr.overtime.employees','planning_id',auto_join=True,index=True,required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',domain="[('area','=',area_id),('branch_id','=',branch_id),('state','=','approved')]")
    company_id = fields.Many2one('res.company', string="Company Name", index=True)
    request_day_name = fields.Char('Request Day Name', compute='_compute_req_day_name', store=True)
    count_record_employees = fields.Integer(string="Total Employees on The List", compute="_compute_record_employees", store=True)


    @api.onchange('periode_id')
    def _onchange_periode_id(self):
        """Update area_id and branch_id based on periode_id and apply dynamic domain."""
        if self.periode_id:
            # Set default values for area_id and branch_id
            self.area_id = self.periode_id.area_id.id if self.periode_id.area_id else False
            self.branch_id = self.periode_id.branch_id.id if self.periode_id.branch_id else False
            # import pdb
            # pdb.set_trace()
            # self.area_id = [('id', '=', self.periode_id.area_id.id)]
            # self.branch_id = [('id', '=', self.periode_id.branch_id.id)]
            # _logger.info("Domain for area_id: %s", self.area_id)
            # _logger.info("Domain for branch_id: %s", self.branch_id)

            # Apply dynamic domains for area_id and branch_id
            # return {
            #     'domain': {
            #         'area_id': domain_area,
            #         'branch_id': domain_branch,
            #     }
            # }
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
            if record.hr_ot_planning_ids:
                raise ValidationError(
                    _("You cannot delete this record as it has related detail records.")
                )
        return super(HREmpOvertimeRequest, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                area_id = vals.get('area_id')
                branch_id = vals.get('branch_id')

                # Fetch area and branch if missing
                if not area_id or not branch_id:
                    periode_id = vals.get('periode_id')
                    if periode_id:
                        periode = self.env['hr.opening.closing'].sudo().search([('id', '=', int(periode_id))], limit=1)
                        if periode:
                            area_id = periode.area_id.id
                            branch_id = periode.branch_id.id
                            vals['area_id'] = area_id
                            vals['branch_id'] = branch_id

                # Fetch related records for generating 'name'
                department_id = vals.get('department_id')
                area = self.env['res.territory'].sudo().search([('id', '=', int(area_id))], limit=1)
                department = self.env['hr.department'].sudo().search([('id', '=', int(department_id))], limit=1)
                branch = self.env['res.branch'].sudo().search([('id', '=', int(branch_id))], limit=1)

            # Validate necessary data and generate 'name'
            if area and department and branch:
                department_code = department.department_code
                branch_unit_id = branch.unit_id
                tgl = fields.Date.today()
                tahun = str(tgl.year)[2:]
                bulan = str(tgl.month)
                sequence_code = self.env['ir.sequence'].next_by_code('hr.overtime.planning')
                vals['name'] = f"{tahun}/{bulan}/{branch_unit_id}/RA/{department_code}/{sequence_code}"
                # res = super(HREmpOvertimeRequest,self).create(vals_list)

        return super(HREmpOvertimeRequest, self).create(vals_list)
    
    def btn_approved(self):
        for rec in self:
            if rec.approve1 == True and rec.approve2 == True and rec.approve3 == True:
                rec.state = 'approved'
            else:
                raise UserError('Approve Not Complete')
    
    def btn_done(self):
        for rec in self:
            rec.state = 'done'

    @api.model
    def _get_visible_states(self):
        """Menentukan state mana yang akan ditampilkan berdasarkan state saat ini"""
        self.ensure_one()
        if self.state == '':
            return 'draft,approved_mgr,done,reject'
        elif self.state == 'draft':
            return 'draft,approved_mgr,done,reject'
        elif self.state == 'approved_mgr':
            return 'draft,approved_mgr,done,reject'
        elif self.state == 'approved_pmr':
            return 'draft,approved_pmr,done,reject'
        elif self.state == 'approved':
            return 'draft,approved,done,reject'
        elif self.state == 'done':
            return 'draft,done,reject'
        elif self.state == 'reject':
            return 'draft,done,reject'
        else:
            return 'draft,approved_mgr,approved_pmr,approved,done,reject'

    def btn_approved_mgr(self):
        for rec in self:
            rec.state = 'approved_mgr'
            
    def btn_approved_pmr(self):
        for rec in self:
            rec.state = 'approved_pmr'
    
    def btn_reject(self):
        for rec in self:
            rec.state = 'reject'
    
    def btn_backdraft(self):
        for rec in self:
            rec.state = 'draft'

    def btn_print_pdf(self):
        return self.env.ref('sanbe_hr_tms.overtime_request_report').report_action(self)   

    
    def get_dynamic_numbers(self):
        """ Menghasilkan nomor urut untuk digunakan dalam QWeb report. """
        numbering = {}
        counter = 1
        for record in self:
            numbering[record.id] = list(range(counter, counter + len(record.hr_ot_planning_ids))) #perbaikan disini
            counter += len(record.hr_ot_planning_ids)
        return numbering        
            
    def action_search_employee(self):
        #if self.department_id:
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _('Search Employee'),
        #     'res_model': 'hr.employeedepartment',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'context': {
        #         'active_id': self.id, 
        #         'fieldname':'plan_id', 
        #         'default_modelname':'hr.overtime.planning',
        #         'default_area_id':self.area_id.id,
        #         'default_branch_id':self.branch_id.id,
        #         'default_plann_date_from':self.periode_from,
        #         'default_plann_date_to':self.periode_to,
        #         'default_department_id':self.department_id.id,
        #         'default_division_id':self.division_id.id,
        #         'default_hrms_department_id':self.hrms_department_id.id,
        #         'default_directorate_id':self.directorate_id.id,
        #         },
        #     'views': [[False, 'form']]
        # }
        #else:
        #    raise UserError('Sub Department Not Selected')
        wizard = self.env['hr.employeedepartment'].create({
                    'plan_id': self.id,
                    'modelname':'hr.overtime.planning',
                    'area_id':self.area_id.id,
                    'branch_id':self.branch_id.id,
                    'department_id':self.department_id.id,
                    'division_id':self.division_id.id,
                    'hrms_department_id':self.hrms_department_id.id,
                    'directorate_id':self.directorate_id.id,
                    'plann_date_from':self.periode_from,
                    'plann_date_to':self.periode_to,
                    })
        emp_line = self.env['hr.employeedepartment.details'].search([('cari_id','=',wizard.id)])
        if not emp_line:
            wizard._isi_employee()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Search Employee'),
            'res_model': 'hr.employeedepartment',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard.id,
            'domain': [('division_id', '=', self.division_id.id),('hrms_department_id', '=', self.hrms_department_id.id),('directorate_id', '=', self.directorate_id.id)],
            'views': [[False, 'form']]
        }
        
        
    def action_generate_ot(self):
        try:
            self.env.cr.execute("CALL generate_ot_request()")
            self.env.cr.commit()
            _logger.info("Stored procedure executed successfully.")
        except Exception as e:
            _logger.error("Error calling stored procedure: %s", str(e))
            raise UserError("Error executing the function: %s" % str(e))

    @api.depends('request_date')
    def _compute_req_day_name(self):
        for record in self:
            if record.request_date:
                record.request_day_name = record.request_date.strftime('%A')
            else:
                record.request_day_name = False

    @api.depends('hr_ot_planning_ids')
    def _compute_record_employees(self):
        for record in self:
            record.count_record_employees = len(record.hr_ot_planning_ids)   
            
    
class HREmpOvertimeRequestEmployee(models.Model):
    _name = "hr.overtime.employees"
    _description = 'HR Employee Overtime Planning Request Employee'

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]
            
    @api.depends('area_id', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id', '=', allrecs.branch_id.id),('active','=',True)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]
            
    @api.depends('areah_id','branchh_id','departmenth_id')
    def _ambil_employee(self):
        for rec in self:
            if rec.areah_id:
                emp = self.env['hr.employee'].sudo().search([('area','=',rec.areah_id.id)])
                if rec.branchh_id:
                    emp = emp.filtered(lambda p:p.branch_id.id == rec.branchh_id.id)
                if rec.departmenth_id:
                    emp = emp.filtered(lambda p:p.department_id.id == rec.departmenth_id.id)
                rec.employee_ids = [Command.set(emp.ids)]

    branch_ids = fields.Many2many('res.branch', 'hr_permission_entry_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    alldepartment = fields.Many2many('hr.department','hr_employeelist_schedule_rel', string='All Department',compute='_isi_department_branch',store=False)
    planning_id = fields.Many2one('hr.overtime.planning',string='HR Overtime Request Planning',index=True)
    areah_id = fields.Many2one('res.territory', string='Area ID Header', related='planning_id.area_id',index=True, readonly=True)
    area_id = fields.Many2one('res.territory', string='Area',index=True)
    branchh_id = fields.Many2one('res.branch', related='planning_id.branch_id',string='Bisnis Unit Header', index=True, readonly=True)
    departmenth_id = fields.Many2one('hr.department', related='planning_id.department_id',string='Department ID Header', index=True, readonly=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='planning_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', related='planning_id.hrms_department_id',store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='planning_id.directorate_id',store=True)
    nik = fields.Char('Employee NIK',index=True)
    employee_ids = fields.Many2many('hr.employee','ov_plan_emp_rel',compute='_ambil_employee',string='Employee Name',store=False)
    employee_id = fields.Many2one('hr.employee',domain="[('id','in',employee_ids),('state','=','approved')]",string='Employee Name',index=True)
    plann_date_from = fields.Date('Plan Date From')
    plann_date_to = fields.Date('Plan Date To')
    ot_plann_from = fields.Float('OT Plan From')
    ot_plann_to = fields.Float('OT Plan To')
    approve_time_from = fields.Float('OT App From')
    approve_time_to = fields.Float('OT App To')
    machine = fields.Char('Machine')
    work_plann = fields.Char('Work Plan')
    output_plann = fields.Char('Output Plan')
    branch_id = fields.Many2one('res.branch', domain="[('id','in',branch_ids)]", string='Business Unit', index=True)
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    bundling_ot = fields.Boolean(string="Bundling OT")
    transport = fields.Boolean('Transport')
    meals = fields.Boolean(string='Meal Dine In')
    meals_cash = fields.Boolean(string='Meal Cash')
    ot_type = fields.Selection([('regular','Regular'),('holiday','Holiday')],string='OT Type')
    planning_req_name = fields.Char(string='Planning Request Name',required=False)

    @api.onchange('employee_id')
    def rubah_employee(self):
        for rec in self:
            if rec.employee_id:
                emp = self.env['hr.employee'].sudo().search([('id','=',rec.employee_id.id)],limit=1)
                if emp:
                    rec.nik = emp.nik
                    #rec.branch_id = emp.branch_id.id
                    #rec.department_id = emp.department_id.id
                    #rec.area_id = emp.area.id

    @api.constrains('nik','plann_date_from','plann_date_to')
    def check_duplicate_record(self):
        for rec in self:
            '''Method to avoid duplicate overtime request'''
            duplicate_record = self.search([
                ('id', '!=', rec.id),
                ('nik','=',rec.nik),
                ('plann_date_from','=',rec.plann_date_from),
                ('plann_date_to','=',rec.plann_date_to),
            ])
            if duplicate_record:
                raise ValidationError(f"Duplicate record found for employee {rec.employee_id.name} in {rec.planning_id.name}. "
                                      f"Start date: {rec.plann_date_from} and end date: {rec.plann_date_to}.")

    @api.model
    def create(self, vals):
        # Add the duplicate check before creating a new record
        self.check_duplicate_record()
        return super(HREmpOvertimeRequestEmployee, self).create(vals)

    def write(self, vals):
        # Add the duplicate check before updating a record
        res = super(HREmpOvertimeRequestEmployee, self).write(vals)
        self.check_duplicate_record()
        return res