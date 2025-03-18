# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
    number = fields.Char('Contract Number')
    area = fields.Many2one('res.territory',string='Area',tracking=True,readonly=False)
    branch_ids = fields.Many2many('res.branch','res_branch_rel',string='AllBranch',compute='_isi_semua_branch',store=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True, domain="[('state','not in',['hold'])]", index=True)
    date_end = fields.Date('End Date', tracking=True, help="End date of the contract (if it's a fixed-term contract).", required=True)
    alldepartment = fields.Many2many('hr.department','hr_department_rel', string='All Department',compute='_isi_department_branch',store=False)
    branch_id = fields.Many2one('res.branch',string='Business Units',domain="[('id','in',branch_ids)]",tracking=True,readonly=False)
    depart_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]",string='Sub Department' )
    wage = fields.Monetary('Wage', required=False, tracking=True, help="Employee's monthly gross wage.", group_operator="avg")
    ws_month = fields.Integer('Working Service Month', compute="_compute_service_duration_display",readonly=True)
    ws_year  = fields.Integer('Working Service Year', compute="_compute_service_duration_display",readonly=True)
    ws_day = fields.Integer('Working Service Day', compute="_compute_service_duration_display",readonly=True)
    nilai_pa = fields.Char('Nilai PA')
    sallary_amount = fields.Monetary('Sallary Amount')
    nik = fields.Char('Nik')
    nik_lama = fields.Char('Nik Lama')
    emp_id = fields.Char('Employee ID',related='employee_id.employee_id',readonly=True)
    emp_name = fields.Char('Employee Name',related='employee_id.name',readonly=True)
    no_pkwt = fields.Selection([('1','1'),
                                ('2','2'),
                                ('3','3'),
                                ('4','4'),
                                ('5','5')],string='# of PKWT',ondelete='cascade')
    # @api.model
    # def name_create(self, name):
    #     default_type = self._context.get('employee_name')
    #     create_values = {self._rec_name: name}
    #     partner = self.create(create_values)
    #     print('name create')
    #     return partner.id, partner.display_name
    _sql_constraints = [
        ('contract_code_unique', 'UNIQUE(name)', 'A Contract must have a unique name.'),
    ]

    # @api.model
    # def create(self, vals):
    #     check_contract = self.env['hr.contract'].search(
    #         [('employee_id', '=', vals.get('employee_id')),
    #          #  ('state', '!=', 'close')
    #          ('state', '=', 'open')
    #          ], limit=1)
        
    #     if check_contract:
    #         raise UserError('A contract with the same employee is already active. You cannot create another contract for the same employee.')
        
    #     return super(HrContract, self).create(vals)

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
            contract.depart_id = contract.employee_id.department_id
            contract.resource_calendar_id = contract.employee_id.resource_calendar_id
            contract.company_id = contract.employee_id.company_id
            contract.area = contract.employee_id.area.id
            contract.branch_id = contract.employee_id.branch_id.id
            contract.nik = contract.employee_id.nik
            contract.nik_lama = contract.employee_id.nik_lama

    def write(self,vals_list):
        res = super(HrContract,self).write(vals_list)
        for allrec in self:
            if allrec.state =='open':
                if allrec.employee_id.state !='approved':
                    raise UserError('Cannot Running Contract Because The Employee Not Yet Being Approved!')
                empstatus = ''
                empstatus = allrec.employee_id.emp_status
                allrec.employee_id.contract_id = allrec.id
                allrec.employee_id.contract_datefrom = allrec.date_start
                allrec.employee_id.contract_dateto = allrec.date_end
                mycari = self.env['hr.employment.log'].sudo().search([('employee_id','=',allrec.employee_id.id),('job_status','=','contract'),('service_type','=', allrec.contract_type_id.code),('start_date','=',allrec.date_start),('end_date','=', allrec.date_end)])
                if not mycari:
                    self.env['hr.employment.log'].sudo().create({'employee_id': allrec.employee_id.id,
                                                                 'service_type': allrec.contract_type_id.code,
                                                                 'start_date': allrec.date_start,
                                                                 'end_date': allrec.date_end,
                                                                 'bisnis_unit': allrec.branch_id.id,
                                                                 'department_id': allrec.depart_id.id,
                                                                 'job_title': allrec.job_id.name,
                                                                 'job_status': 'contract',
                                                                 'emp_status': empstatus,
                                                                 'model_name': 'hr.contract',
                                                                 'model_id': allrec.id,
                                                                 'doc_number': allrec.name,
                                                                 })


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

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
               group_name = self.env['res.groups'].search([('name','=','HRD CA')])
               cekgroup = self.env.user.id in group_name.users.ids
               if cekgroup:
                   for node in arch.xpath("//field"):
                          node.set('readonly', 'True')
                   for node in arch.xpath("//button"):
                          node.set('invisible', 'True')
        return arch, view

    @api.model
    def default_get(self, default_fields):
        res = super(HrContract, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res