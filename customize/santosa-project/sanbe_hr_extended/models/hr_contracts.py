# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    @api.depends('area','branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id','=', allrecs.branch_id.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]


    attachment_contract =  fields.Many2many('ir.attachment', 'hr_contract_rel',string='Contract Document',
                                          help="You may attach files to with this")
    number = fields.Char('No. Kontrak')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    alldepartment = fields.Many2many('hr.department', 'hr_department_rel', string='All Department',
                                     compute='_isi_department_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', tracking=True,  default=lambda self: self.env.user.branch_id, required=True)
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Nama Karyawan', 
        required=True, 
        tracking=True, 
        domain=lambda self: [
            ('state', 'not in', ['hold']),
            ('job_status', 'in', ['contract', 'partner_doctor']),
        ], 
        index=True
    )                 
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    employee_group1s = fields.Many2one('emp.group', string='Employee P Group', related='employee_id.employee_group1s', store=True)
    work_unit_id = fields.Many2one('hr.work.unit','Work Unit', related='employee_id.work_unit_id', store=True)
    work_unit = fields.Char(related='employee_id.work_unit', string='Unit Kerja', store=True)
    medic = fields.Many2one('hr.profesion.medic','Profesi Medis', related='employee_id.medic', store=True)
    nurse = fields.Many2one('hr.profesion.nurse','Profesi Perawat', related='employee_id.nurse', store=True)
    job_id = fields.Many2one('hr.job','Jabatan', related='employee_id.job_id', readonly=True, store=True)
    seciality = fields.Many2one('hr.profesion.special','Kategori Khusus', related='employee_id.seciality', store=True)
    
    department_id = fields.Many2one('hr.department', compute = '_find_department_id',  string='Departemen', store=True, related='employee_id.department_id')
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', related='employee_id.hrms_department_id', store=True)
    
    @api.depends('hrms_department_id')
    def _find_department_id(self):
        for line in self:
            if line.hrms_department_id:
                Department = self.env['hr.department'].search(['|',('name', '=', line.division_id.name),('name', 'ilike', line.division_id.name)], limit=1)
                if Department:
                    line.department_id = Department.id
                else:
                    Department = self.env['hr.department'].sudo().create({
                        'name': line.hrms_department_id.name,
                        'active': True,
                        'company_id': self.env.user.company_id.id,
                    })
                    line.department_id = Department.id

    alldepartment = fields.Many2many('hr.department','hr_department_rel', string='All Department',compute='_isi_department_branch',store=False)
    depart_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]",string='Sub Department' )
    
    date_end = fields.Date('End Date', tracking=True, help="End date of the contract (if it's a fixed-term contract).", required=True)
    wage = fields.Monetary('Wage', required=False, tracking=True, help="Employee's monthly gross wage.", group_operator="avg")
    ws_month = fields.Integer('Working Service Month', compute="_compute_service_duration_display",readonly=True)
    ws_year  = fields.Integer('Working Service Year', compute="_compute_service_duration_display",readonly=True)
    ws_day = fields.Integer('Working Service Day', compute="_compute_service_duration_display",readonly=True)
    nilai_pa = fields.Char('Nilai PA')
    sallary_amount = fields.Monetary('Sallary Amount')
    nik = fields.Char('Nik')
    nik_lama = fields.Char('Nik Lama')
    emp_id = fields.Char('ID Karyawan',related='employee_id.employee_id',readonly=True)
    emp_name = fields.Char('Nama Karyawan',related='employee_id.name',readonly=True)
    no_pkwt = fields.Selection([('1','1'),
                                ('2','2'),
                                ('3','3'),
                                ('4','4'),
                                ('5','5')],string='# of PKWT',ondelete='cascade')

    # user_id = fields.Many2one(comodel_name='res.users', string="User", 
    #                           default=lambda self: self.env.user, readonly=True)

    _sql_constraints = [
        ('contract_code_unique', 'UNIQUE(name)', 'A Contract must have a unique name.'),
    ]

    
    # @api.model
    def unlink(self):
        return super(HrContract, self).unlink()
    
    @api.constrains('name')
    def _contrains_name(self):
        # Prevent a coupon from having the same code a program
        cekktp  = self.env['hr.contract'].sudo().search([('name','=', self.name)])
        if len(cekktp) > 1:
            raise UserError(_('A Contract with the same name already exist.'))

    @api.model
    def default_get(self, default_fields):
        res = super(HrContract, self).default_get(default_fields)
        empname = self._context.get('employee_name')
        isemployee = self._context.get('is_employee')
        if isemployee:
            myemp = self.env['hr.employee'].sudo().search([('name','=', empname)])
            if myemp:
                res.update({'employee_id': myemp.id})
            else:
                myemp = False
                myemp = self.env['hr.employee'].create({'name': empname,
                                                        'area':  self._context.get('area',False),
                                                        'branch_id':  self._context.get('branch',False),
                                                        'department_id':  self._context.get('department',False),
                                                        'job_id':  self._context.get('job_id',False),})
                myemp.write({'name': empname})
                res.update({'employee_id': myemp.id})
        return res

    @api.depends('employee_id','state')
    @api.onchange('employee_id')
    def _compute_employee_contract(self):
        for contract in self.filtered('employee_id'):
            contract.job_id = contract.employee_id.job_id
            contract.resource_calendar_id = contract.employee_id.resource_calendar_id
            contract.company_id = contract.employee_id.company_id
            contract.area = contract.employee_id.area.id
            contract.branch_id = contract.employee_id.branch_id.id
            contract.hrms_department_id = contract.employee_id.hrms_department_id.id
            contract.nik = contract.employee_id.nik
            contract.nik_lama = contract.employee_id.nik_lama

    def write(self,vals_list):
        # res = super(HrContract,self).write(vals_list)
        for allrec in self:
            if allrec.state =='open':
                # if allrec.employee_id.state !='approved':
                #     raise UserError('Cannot Running Contract Because The Employee Not Yet Being Approved!')
                # empstatus = ''
                empstatus = allrec.employee_id.emp_status
                allrec.employee_id.contract_id = allrec.id
                allrec.employee_id.contract_datefrom = allrec.date_start
                allrec.employee_id.contract_dateto = allrec.date_end
                mycari = self.env['hr.employment.log'].sudo().search([
                    ('employee_id','=',allrec.employee_id.id),
                    ('job_status','=','contract'),
                    ('service_type','=', allrec.contract_type_id.code),
                    ('start_date','=',allrec.date_start),
                    ('end_date','=', allrec.date_end)
                    ])
              
                if not mycari:   
                    self.env['hr.employment.log'].sudo().create({'employee_id': allrec.employee_id.id,
                                                                 'service_type': allrec.contract_type_id.code,
                                                                 'start_date': allrec.date_start,
                                                                 'end_date': allrec.date_end,
                                                                 'area': allrec.area.id,
                                                                 'bisnis_unit': allrec.branch_id.id,
                                                                 'directorate_id': allrec.directorate_id.id,
                                                                 'hrms_department_id': allrec.hrms_department_id.id,
                                                                 'division_id': allrec.division_id.id,
                                                                 'job_title': allrec.job_id.name,
                                                                 'job_status': 'contract',
                                                                 'emp_status': empstatus,
                                                                 'model_name': 'hr.contract',
                                                                 'model_id': allrec.id,
                                                                 'doc_number': allrec.name,
                                                                 })
                  
        return super(HrContract, self).write(vals_list)         


    @api.depends("date_start","date_end")
    def _compute_service_duration_display(self):
        for record in self:
            if record.date_start and record.date_end:
                service_until = record.date_end
                if record.date_start and service_until > record.date_start:
                    service_duration = relativedelta(
                        service_until, record.date_start
                    )
                    record.ws_year = service_duration.years
                    record.ws_month = service_duration.months
                    record.ws_day = service_duration.days
                else:
                    record.ws_year = 0
                    record.ws_month = 0
                    record.ws_day = 0
            else:
                record.ws_year = 0
                record.ws_month = 0
                record.ws_day = 0
    #
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            #mybranch = self.env['res.branch'].sudo().search([('branch_code','=','BU3')])
            mybranch = self.env.user.branch_id
            search_domain = [('name', operator, name),('branch_id','=',mybranch.id)]
            user_ids = self._search(search_domain, limit=1, order=order)
            return user_ids
        else:
            return super()._name_search(name, domain, operator, limit, order)

    @api.model
    def default_get(self, default_fields):
        res = super(HrContract, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        
        branch_ids_from_context = self.env.context.get('allowed_branch_ids')

        # Jika allowed_branch_ids tersedia di konteks, gunakan untuk filter
        if branch_ids_from_context:

            # Jika daftar kosong (misalnya, tidak ada cabang yang dicentang), pastikan tidak ada record yang ditampilkan
            if not branch_ids_from_context:
                branch_ids_to_filter = [0] # Gunakan ID 0 atau ID yang pasti tidak ada
                _logger.warning(f"[_search] allowed_branch_ids dari konteks kosong. Mengatur branch_ids_to_filter ke {branch_ids_to_filter}.")
            else:
                branch_ids_to_filter = branch_ids_from_context

            # Tambahkan kondisi domain ke argumen pencarian awal yang digunakan untuk filter data yang ditampilkan
            args = [('branch_id', 'in', branch_ids_to_filter)] + list(args)

        else:
            # Jika allowed_branch_ids tidak tersedia di konteks,
            # maka fallback ke logika sebelumnya (filter berdasarkan allowed_company_ids)
            # atau biarkan tanpa filter dinamis jika tidak ada allowed_company_ids.
            allowed_company_ids = self.env.context.get('allowed_company_ids')

            if allowed_company_ids:

                company_branches = self.env['res.branch'].sudo().search([
                    ('company_id', 'in', allowed_company_ids)
                ])
                branch_ids_from_switcher = company_branches.ids

                if not branch_ids_from_switcher:
                    branch_ids_from_switcher = [0]

                args = [('branch_id', 'in', branch_ids_from_switcher)] + list(args)


        # Setelah ini, record rule Anda (jika ada) akan diterapkan di atas hasil ini.
        # method python lebih kuat dari record rule, bersifat dinamis dibandingkan record rule yang statis
        return super(HrContract, self)._search(args, offset, limit, order, count)