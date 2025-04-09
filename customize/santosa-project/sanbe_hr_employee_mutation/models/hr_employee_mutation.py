from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
import requests
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class HrEmployeeMutation(models.Model):
    _name = 'hr.employee.mutations'
    _description = 'HR Employee Mutation'
    _order = 'create_date desc'

    @api.depends('name')
    def _isi_emps(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for allrecs in self:
            allemps = self.env['hr.employee'].sudo().search(
                [('state', '=', 'approved'), ('active', '=', True), ('branch_id', '=', user.branch_id.id)])
            allrecs.emp_nos_ids = [Command.set(allemps.ids)]

    @api.depends('service_area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.service_area.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    name = fields.Char(
        string="Transaction Number",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    letter_no = fields.Char('Reference Number')
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    idpeg = fields.Char('Employee ID')
    emp_no = fields.Char('Employee No')
    emp_nos_ids = fields.Many2many('hr.employee', 'res_emp_nos_rel', string='AllEmpNos',
                                   compute='_isi_emps', store=False)
    emp_nos = fields.Many2one('hr.employee', string='Employee Number', index=True, domain="[('id','in',emp_nos_ids)]")
    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    employee_name = fields.Char(string='Employee Name')
    nik = fields.Char('NIK')
    area = fields.Char('Area')
    bisnis_unit = fields.Char('Business Unit')
    departmentid = fields.Char(string='Sub Department')
    state = fields.Selection(selection=[('draft', "Draft"),
                                        ('intransfer', "In Transfer"),
                                        ('accept', "Accept"),
                                        ('approved', "Approved")],
                             string="Status", readonly=True,
                             copy=False, index=True,
                             tracking=3, default='draft')
    job_status = fields.Selection([('permanent', 'Permanent'),
                                   ('contract', 'Contract'),
                                   ('outsource', 'Outsource'),
                                   ('visitor', 'Visitor'),
                                   ('mitra', 'Mitra'),
                                   ('tka', 'TKA')],
                                  default='contract', string='Job Status')
    # employementstatus = fields.Char('Employment Status')
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('terminated', 'Terminated'),
                                   ], string='Employment Status', compute='_compute_emp_status', store=True)
    emp_status_actv = fields.Selection([('probation', 'Probation'),
                                        ('confirmed', 'Confirmed')
                                        ], string='Employment Status', store=True)
    emp_status_other = fields.Selection([('confirmed', 'Confirmed')
                                        ], string='Employment Status', store=True)
    job_title = fields.Many2one('hr.job', 'Job Position', check_company=True)
    employee_group1 = fields.Selection(selection=[('Group1', 'Group 1 - Harian(pak Deni)'),
                                                  ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
                                                  ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
                                                  ('Group4', 'Group 4 - Security and non apoteker (bu Susi)'),
                                                  ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
                                                  ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
                                                  ('Group7', 'Group 7 - Tim Proyek (pak Ferry)'), ],
                                       string="Employee P Group")
    service_type = fields.Selection([('conf', 'Confirm'),
                                     ('prom', 'Promotion'),
                                     ('demo', 'Demotion'),
                                     ('rota', 'Rotation'),
                                     ('muta', 'Mutation'),
                                     ('actv', 'Activation'),
                                     ('corr', 'Correction')], string='Service Type', required=True)
    service_date = fields.Date('Transaction Date', default=fields.Date.today())
    service_status = fields.Char('Mutation Status')
    service_nik = fields.Char('NIK')
    service_employee_id = fields.Char('Employee ID', default='New')
    service_no_npwp = fields.Char('NPWP Number')
    service_no_ktp = fields.Char('KTP Number')
    service_area = fields.Many2one('res.territory', string='Area')
    service_bisnisunit = fields.Many2one('res.branch', domain="[('id','in',branch_ids)]", string='Business Unit')
    service_departmentid = fields.Many2one('hr.department', domain="[('branch_id','=',service_bisnisunit)]", string='Sub Department')
    service_identification = fields.Char('Identification Number')
    service_jobstatus = fields.Selection([('permanent', 'Permanent'),
                                          ('contract', 'Contract'),
                                          ('outsource', 'Out Source')],
                                         default='contract', string='Job Status')
    service_employementstatus = fields.Selection([('probation', 'Probation'),
                                                  ('confirmed', 'Confirmed'),
                                                  ('probation', 'Probation'),
                                                  ('end_contract', 'End Of Contract'),
                                                  ('resigned', 'Resigned'),
                                                  ('retired', 'Retired'),
                                                  ('terminated', 'Terminated')],
                                                 string='Employment Status')
    service_jobtitle = fields.Many2one('hr.job', domain="[('department_id','=',service_departmentid)]", string='Job Position', index=True)
    service_empgroup1 = fields.Selection(selection=[('Group1', 'Group 1 - Harian(pak Deni)'),
                                                    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
                                                    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
                                                    ('Group4', 'Group 4 - Security and non apoteker (bu Susi)'),
                                                    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
                                                    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
                                                    ('Group7', 'Group 7 - Tim Proyek (pak Ferry)'), ],
                                         string="Service Employee P Group")
    service_start = fields.Date('Effective Date From', required=True)
    service_end = fields.Date('Effective Date To')
    remarks = fields.Text('Remarks')
    image = fields.Many2many('ir.attachment', string='Image', help="You may attach files to with this")
    employee_level = fields.Char('Employee Level')
    employee_levels = fields.Many2one('employee.level', string='Employee Level')
    service_employee_levels = fields.Many2one('employee.level', string='Employee Level')
    join_date = fields.Date('Join Date')
    marital = fields.Selection([('single', 'Single'),
                                ('married', 'Married'),
                                ('cohabitant', 'Legal Cohabitant'),
                                ('widower', 'Widower'),
                                ('divorced', 'Divorced')], string='Marital Status')
    contract_no = fields.Many2one('hr.contract', related='employee_id.contract_id', readonly=False)
    contract_from = fields.Date('Contract Date From', related='employee_id.contract_datefrom', readonly=False)
    contract_to = fields.Date('Contract Date To', related='employee_id.contract_dateto', readonly=False)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    nik_lama = fields.Char('Previous NIK')
    service_nik_lama = fields.Char('Previous NIK')

    def button_approve(self):
        self.ensure_one()
        # for rec in self:
        #     if rec.service_end == False:
        #         raise UserError('Effective Date To Still Empty')
        self._update_employee_status()
        self.env['hr.employment.log'].sudo().create({'employee_id': self.employee_id.id,
                                                     'service_type': self.service_type.upper(),
                                                     'start_date': self.service_start,
                                                     'end_date': self.service_end,
                                                     'bisnis_unit': self.service_bisnisunit.id,
                                                     'department_id': self.service_departmentid.id,
                                                     'job_title': self.service_jobtitle.name,
                                                     'job_status': self.service_jobstatus,
                                                     'emp_status': self.service_employementstatus,
                                                     'model_name': 'hr.employee.mutations',
                                                     'model_id': self.id,
                                                     'trx_number': self.name,
                                                     'doc_number': self.letter_no,
                                                     })
        # mylogs = self.env['hr.employment.log'].sudo().search(
        #    [('employee_id', '=', self.employee_id.id), ('service_type', '=',self.service_type)])
        # if mylogs:
        #    for alllogs in mylogs:
        #        if alllogs.end_date == False:
        #            alllogs.write({'end_date': self.service_start})
        self.employee_id.write({'state': 'hold'})
        if self.service_area.id != self.employee_id.area.id:
            self.employee_id.write({'area': self.service_area.id})
        if self.service_bisnisunit.id != self.employee_id.branch_id.id:
            query = """ update hr_employee set branch_id = %s where id = %s"""
            self.env.cr.execute((query)%(self.service_bisnisunit.id,self.employee_id.id))
            # self.employee_id.sudo().write({'branch_id': self.service_bisnisunit.id})
        if self.service_departmentid.id != self.employee_id.department_id.parent_id.id:
            self.employee_id.write({'department_id': self.service_departmentid.id})
        if self.service_jobstatus != self.employee_id.job_status:
            self.employee_id.write({'job_status': self.service_jobstatus})
        if self.service_employementstatus != self.employee_id.emp_status:
            self.employee_id.write({'emp_status': self.service_employementstatus})
        if self.service_jobtitle.id != self.employee_id.job_id.id:
            self.employee_id.write({'job_id': self.service_jobtitle.id})
        if self.service_empgroup1 != self.employee_id.employee_group1:
            self.employee_id.write({'employee_group1': self.service_empgroup1})
        # if self.service_employee_id != self.employee_id.employee_id:
        #    self.employee_id.write({'employee_id': self.service_employee_id})
        if self.service_no_npwp != self.employee_id.no_npwp:
            self.employee_id.write({'no_npwp': self.service_no_npwp})
        if self.service_no_ktp != self.employee_id.no_ktp:
            self.employee_id.write({'no_ktp': self.service_no_ktp})
        if self.service_identification != self.employee_id.identification_id:
            self.employee_id.write({'identification_id': self.service_identification})
        if self.service_nik != self.employee_id.nik:
            self.employee_id.write({'nik_lama': self.employee_id.nik})
            self.employee_id.write({'nik': self.service_nik})
            self.nik_lama = self.employee_id.nik_lama
            self.service_nik_lama = self.employee_id.nik_lama
            self.nik = self.employee_id.nik
        if self.join_date != self.employee_id.join_date:
            self.employee_id.write({'join_date': self.join_date})
        if self.marital != self.employee_id.marital:
            self.employee_id.write({'marital': self.marital})
        if self.service_employee_levels != self.employee_id.employee_levels:
            self.employee_id.write({'employee_levels': self.service_employee_levels})
        # if self.service_nik_lama != self.employee_id.nik_lama:
        #     self.employee_id.write({'nik_lama': self.service_nik_lama})
        # if not mylogs:
        self.employee_id.write({'state': 'approved'})

        return self.write({'state': 'approved',
                           'service_status': 'Approved'})

    def button_intransfer(self):
        self.write({'state': 'intransfer'})
        return True

    def button_accept(self):
        self.write({'state': 'accept'})
        return True
    
    def print_fkpm_action_button(self):
        """ Print report FKPM """
        return self.env.ref('sanbe_hr_employee_mutation.fkpm_report').report_action(self)


    def pencarian_data(self):
        return
    
    def _update_employee_status(self):
        for record in self:
            if record.emp_status and record.employee_id:
                record.service_employementstatus = self.emp_status
                new_emp_status_id = self.env['hr.emp.status'].sudo().search([('emp_status', '=', self.emp_status),('status', '=', False)])
                if new_emp_status_id:
                    record.employee_id.sudo().write({'emp_status_id': new_emp_status_id.id})

    def write(self, vals):
        res = super(HrEmployeeMutation, self).write(vals)
        for rec in self:
            myemp = rec.emp_nos
            if rec.state == 'draft':
                myemp.write({'state': 'hold'})
            else:
                myemp.write({'state': 'approved'})
        return res

    @api.depends('emp_status_actv', 'emp_status_other', 'service_type')
    def _compute_emp_status(self):
        if self.service_type in ['actv']:
            self.emp_status = self.emp_status_actv
        elif self.service_type not in ['actv','corr']:
            self.emp_status = self.emp_status_other
        # else:
        #     self.emp_status 
        print(self.emp_status_actv, "1")
        print(self.emp_status_other, "2")
        print(self.emp_status, "3")

    @api.onchange('emp_nos')
    def isi_data_employee(self):
        for existing in self:
            if not existing.emp_nos:
                return
            myemp = existing.emp_nos
            empgroup = existing.emp_nos.employee_group1
            if existing.state == 'draft':
                myemp.write({'state': 'hold'})
            else:
                myemp.write({'state': 'approved'})
            existing.service_identification = myemp.identification_id
            existing.emp_no = myemp.employee_id
            existing.nik = str(myemp.nik)
            existing.employee_id = myemp.id
            existing.employee_name = myemp.name
            existing.area = myemp.area.name
            existing.bisnis_unit = myemp.branch_id.name
            existing.departmentid = myemp.department_id.name
            existing.job_status = myemp.job_status
            existing.emp_status = myemp.emp_status
            existing.job_title = myemp.job_id.id
            existing.employee_group1 = myemp.employee_group1
            existing.service_nik = str(str(myemp.nik).replace("('", '')).replace("')", "")
            existing.service_nik_lama = str(str(myemp.nik_lama).replace("('", '')).replace("')", "")
            existing.nik_lama = existing.service_nik_lama
            existing.service_area = myemp.area.id
            existing.service_bisnisunit = myemp.department_id.branch_id.id or myemp.branch_id.id
            existing.service_departmentid = myemp.department_id.id
            existing.service_jobstatus = myemp.job_status
            existing.service_employementstatus = 'confirmed'  # myemp.emp_status
            existing.service_jobtitle = myemp.job_id.id
            existing.service_employee_levels = myemp.employee_levels.id
            existing.employee_levels = myemp.employee_levels.id
            # existing.service_empgroup = empgroup
            existing.service_empgroup1 = myemp.employee_group1

            existing.service_employee_id = myemp.employee_id
            existing.service_no_npwp = myemp.no_npwp
            existing.service_no_ktp = myemp.no_ktp
            existing.join_date = myemp.join_date
            existing.marital = myemp.marital

            existing.service_status = 'Draft'

    @api.model
    def _cron_sync_mutation_data(self, work_days=None):
        mysearch = self.env['hr.employee'].search([])
        for alldata in mysearch:
            mycari = self.env['hr.employee.mutations'].sudo().search([('service_start', '=', date.today())])
            if mycari:
                employee = False
                for allcari in mycari:
                    employee = self.env['hr.employee'].sudo().browse(allcari.employee_id.id)
                    if employee:
                        if allcari.service_area.id != employee.area.id:
                            employee.write({'area': allcari.service_area.id})
                        elif allcari.service_bisnisunit.id != employee.branch_id.id:
                            employee.write({'branch_id': allcari.service_bisnisunit.id})
                        elif allcari.service_departmetid.id != employee.department_id.parent_id.id:
                            employee.write({'department_id': allcari.service_departmentid.id})
                        elif allcari.service_jobstatus != employee.job_status:
                            employee.write({'job_status': allcari.servicejobstatus})
                        elif allcari.service_employementstatus != employee.emp_status:
                            employee.write({'emp_status': allcari.service_employementstatus})
                        elif allcari.service_jobtitle.id != employee.job_id.id:
                            employee.write({'job_id': allcari.service_jobtitle.id})
                        elif allcari.service_empgroup != employee.employee_group1:
                            employee.write({'employee_group1': allcari.service_empgroup})
                        elif allcari.service_employee_id != employee.employee_id:
                            employee.write({'employee_id': allcari.service_employee_id})
                        elif allcari.service_no_npwp != employee.no_npwp:
                            employee.write({'no_npwp': allcari.service_no_npwp})
                        elif allcari.service_no_ktp != employee.no_ktp:
                            employee.write({'no_ktp': allcari.service_no_ktp})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.employee.mutations') or _('New')
        res = super(HrEmployeeMutation, self).create(vals)
        for allres in res:
            employee = self.env['hr.employee'].sudo().browse(allres.employee_id.id)
            employee.write({'state': 'hold'})
        return res

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view


class HrEmployee(models.Model):
    """Extended model for HR employees with additional features."""
    _inherit = 'hr.employee'

    @api.model
    def get_all_ids(self):
        myhr = self.env['hr.employee'].sudo().search([])
        return myhr.ids

    @api.model
    def get_all_emp_byid(self, idemp):
        empid = str(str(idemp).replace('[', '')).replace(']', '')
        myemp = self.env['hr.employee'].sudo().browse(int(empid))
        empgroup = myemp.employee_group1
        datahr = {
            'emp_no': myemp.employee_id,
            'nik': myemp.nik,
            'employee_id': [myemp.id, myemp.name],
            'employee_name': myemp.name,
            'area': myemp.area.name,
            'bisnis_unit': myemp.department_id.branch_id.name,
            'departmentid': myemp.department_id.name,
            'subdepartment': myemp.department_id.parent_id.name or '',
            'jobstatus': myemp.job_status,
            'employementstatus': myemp.emp_status,
            'jobtitle': myemp.job_id.name,
            'empgroup': empgroup,
            'service_nik': myemp.nik,
            'service_area': [myemp.area.id, myemp.area.name],
            'service_bisnisunit': [myemp.department_id.branch_id.id, myemp.department_id.branch_id.name],
            'service_departmentid': [myemp.department_id.id, myemp.department_id.name],
            'service_jobstatus': myemp.job_status,
            'service_employementstatus': myemp.emp_status,
            'service_jobtitle': [myemp.job_id.id, myemp.job_id.name],
            'service_empgroup': empgroup,
            'bond_service': myemp.bond_service,
            'service_from': myemp.service_from,
            'service_to': myemp.service_to,
        }
        return datahr

