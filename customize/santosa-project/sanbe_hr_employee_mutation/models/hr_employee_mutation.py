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


    name = fields.Char(
        string="Transaction Number",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    
    letter_no = fields.Char('Reference Number')
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    idpeg = fields.Char('Employee ID')
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', index=True)
    emp_id = fields.Char(string='ID Karyawan', tracking=True)
    nik = fields.Char(string='NIK', tracking=True)
    area = fields.Many2one('res.territory', string='Area', tracking=True)
    alldepartment = fields.Many2many('hr.department', 'hr_department_rel', string='All Department',  store=False)                
    branch_id = fields.Many2one('res.branch', string='unit Bisnis', domain="[('id','in',branch_ids)]", tracking=True)     
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', tracking=True)
    division_id = fields.Many2one('sanhrms.division', string='Divisi', tracking=True)
    employee_group1s = fields.Many2one('emp.group', string='Employee P Group', tracking=True)
    work_unit_id = fields.Many2one('hr.work.unit', string='Work Unit', tracking=True)
    work_unit = fields.Char(string='Unit Kerja')
    parent_id = fields.Many2one('parent.hr.employee', string='Atasan Langsung', tracking=True)
    parent_nik = fields.Char(related='parent_id.nik', string='NIK Atasan', tracking=True)
    medic = fields.Many2one('hr.profesion.medic', string='Profesi Medis', tracking=True)
    nurse = fields.Many2one('hr.profesion.nurse', string='Profesi Perawat', tracking=True)
    job_id = fields.Many2one('hr.job', string='Jabatan', tracking=True)
    speciality = fields.Many2one('hr.profesion.special', string='Kategori Khusus',tracking=True)
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen', tracking=True)
    employee_levels = fields.Many2one('employee.level', string='Employee Level', tracking=True)
    state = fields.Selection(selection=[('draft', "Draft"),
                                        # ('intransfer', "In Transfer"),
                                        # ('accept', "Accept"),
                                        ('approved', "Approved")],
                             string="Status", readonly=True,
                             copy=False, index=True,
                             tracking=3, default='draft')
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], default='contract', tracking=True, related="employee_id.job_status", string='Status Hubungan Kerja')
    emp_status = fields.Selection(related='employee_id.emp_status', string='Status Karyawan', store=True)
    emp_status_otheremp_status_actv = fields.Selection([
                                        ('confirmed', 'Confirmed')
                                        ], string='Status Karyawan', default='confirmed', store=True)
    emp_status_other = fields.Selection([('confirmed', 'Confirmed')
                                        ], string='Status Karyawan',default='confirmed', store=True)
    emp_status_actv = fields.Selection([('probation', 'Probation'),
                                        ('confirmed', 'Confirmed')
                                        ], string='Status Karyawan',default='confirmed', store=True)
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
                                     ('corr', 'Correction')], default = 'conf', string='Service Type', required=True)
    service_date = fields.Date('Transaction Date', default=fields.Date.today())
    service_status = fields.Char('Mutation Status')
    service_nik = fields.Char('NIK', default=lambda self:self.employee_id.nik)
    service_birthday = fields.Date('Tanggal lahir', default=lambda self:self.employee_id.birthday)
    service_employee_id = fields.Char('Employee ID', default='New')
    service_no_npwp = fields.Char('Nomor NPWP', default=lambda self:self.employee_id.no_npwp)
    service_no_ktp = fields.Char('Nomor KTP', default=lambda self:self.employee_id.no_ktp)
    service_area = fields.Many2one('res.territory', string='Area', tracking=True)
    service_bisnisunit = fields.Many2one('res.branch', domain="[('id','in',branch_ids)]", string='Unit Bisnis', default=lambda self:self.branch_id.id)              
    service_division_id = fields.Many2one('sanhrms.division',string='Divisi', default=lambda self:self.employee_id.division_id.id)
    service_directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', default=lambda self:self.employee_id.directorate_id.id)
    service_employee_group1s = fields.Many2one('emp.group', string='Employee P Group', default=lambda self:self.employee_id.employee_group1s.id)
    service_work_unit_id = fields.Many2one('hr.work.unit','Work Unit', default=lambda self:self.employee_id.work_unit_id.id)
    service_medic = fields.Many2one('hr.profesion.medic','Profesi Medis', default=lambda self:self.employee_id.medic.id)
    service_nurse = fields.Many2one('hr.profesion.nurse','Profesi Perawat', default=lambda self:self.employee_id.nurse.id)
    service_speciality = fields.Many2one('hr.profesion.special','Kategori Khusus', default=lambda self:self.employee_id.seciality.id)
    service_departmentid = fields.Many2one('sanhrms.department', domain="[('branch_id','=',service_bisnisunit)]", string='Departemen', default=lambda self:self.employee_id.hrms_department_id.id)
    service_identification = fields.Char(related='employee_id.identification_id', string='Nomor Kartu Keluarga', store=True)
    service_jobstatus = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], tracking=True, string='Status Hubungan Kerja', default=lambda self:self.employee_id.job_status )
    service_job_status_id = fields.Many2one('sanhrms.job.status', string='Status Pekerjaan', default=lambda self:self.employee_id.job_status)
    service_job_status_type = fields.Selection(store=True, default=lambda self:self.employee_id.job_status, related='service_job_status_id.type')
    service_employementstatus = fields.Selection([('probation', 'Probation'),
                                                  ('confirmed', 'Confirmed'),
                                                  ('end_contract', 'End Of Contract'),
                                                  ('resigned', 'Resigned'),
                                                  ('retired', 'Retired'),
                                                  ('terminated', 'Terminated')],
                                                 string='Status Kekaryawanan')
    service_jobtitle = fields.Many2one('hr.job', domain="[('hrms_department_id','=',service_departmentid)]", string='Jabatan', index=True, default=lambda self:self.employee_id.job_id.id)
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
    service_name = fields.Char('Nama Karyawan')
    service_previous_name = fields.Char('Nama Karyawan Sebelumnya')
    remarks = fields.Text('Remarks')
    image = fields.Many2many('ir.attachment', string='Image', help="You may attach files to with this")
    service_employee_levels = fields.Many2one('employee.level', string='Employee Level', default=lambda self:self.employee_id.employee_levels.id)
    join_date = fields.Date('Join Date')
    marital = fields.Selection([('single', 'Lajang'),
                            ('married', 'Menikah'),
                            ('seperate', 'Berpisah')], string='Status Pernikahan')
    contract_no = fields.Many2one('hr.contract', related='employee_id.contract_id', readonly=False)
    contract_from = fields.Date('Contract Date From', related='employee_id.contract_datefrom', readonly=False)
    contract_to = fields.Date('Contract Date To', related='employee_id.contract_dateto', readonly=False)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    nik_lama = fields.Char('NIK Lama', store=True)
    service_nik_lama = fields.Char('Previous NIK', default=lambda self:self.employee_id.nik)


    @api.depends('hrms_department_id')
    def _find_department_id(self):
        for line in self:
            if line.hrms_department_id:
                Department = self.env['sanhrms.department'].search([('name', 'ilike', line.division_id.name)], limit=1)
                if Department:
                    line.hrms_department_id = Department.id
                else:
                    Department = self.env['hr.department'].sudo().create({
                        'name': line.hrms_department_id.name,
                        'active': True,
                        'company_id': self.env.user.company_id.id,
                    })
                    line.hrms_department_id = Department.id

    @api.depends('service_area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.service_area.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    def unlink(self):
        return super(HrEmployeeMutation, self).unlink()

    def button_approve(self):
        self.ensure_one()
        self._update_employee_status()
        self.env['hr.employment.log'].sudo().create({'employee_id': self.employee_id.id,
                                                     'service_type': self.service_type.upper(),
                                                     'start_date': self.service_start,
                                                     'end_date': self.service_end,
                                                     'area': self.service_area.id,
                                                     'bisnis_unit': self.service_bisnisunit.id,
                                                     'directorate_id': self.service_directorate_id.id,
                                                     'hrms_department_id': self.service_departmentid.id,
                                                     'division_id': self.service_division_id.id,
                                                     'job_title': self.service_jobtitle.name,
                                                     'job_status': self.service_jobstatus,
                                                     'emp_status': self.service_employementstatus,
                                                     'model_name': 'hr.employee.mutations',
                                                     'model_id': self.id,
                                                     'trx_number': self.name,
                                                     'doc_number': self.letter_no,
                                                     })

        
        if self.service_area.id != self.employee_id.area.id:
            self.employee_id.write({'area': self.service_area.id})
        
        if self.service_bisnisunit and self.service_bisnisunit.id != self.employee_id.branch_id.id:
            self.employee_id.write({'branch_id': self.service_bisnisunit.id})
        elif not self.service_bisnisunit:
            raise UserError("Unit Bisnis (branch_id) wajib diisi sebelum approval.")

        if self.service_directorate_id != self.employee_id.directorate_id.id:
            self.employee_id.write({'directorate_id': self.service_directorate_id.id})

        if self.service_departmentid.id != self.employee_id.hrms_department_id.id:
            self.employee_id.write({'hrms_department_id': self.service_departmentid.id})

        if self.service_division_id.id != self.employee_id.division_id.id:
            self.employee_id.write({'division_id': self.service_division_id.id})

        if self.service_jobstatus != self.employee_id.job_status:
            self.employee_id.write({'job_status': self.service_jobstatus})

        if self.service_jobstatus != self.employee_id.job_status:
            self.employee_id.write({'job_status': self.service_jobstatus})

        if self.service_type == 'conf':
            self.employee_id.write({'emp_status': 'confirmed'})
        elif self.service_type in ['actv','corr']:
            if self.emp_status_actv != self.employee_id.emp_status:
                self.employee_id.write({'emp_status': self.emp_status_actv})
        else:            
            self.employee_id.write({'emp_status': 'confirmed'})

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

        if self.service_medic != self.employee_id.medic:
            self.employee_id.write({'medic': self.service_medic})

        if self.service_nurse != self.employee_id.nurse:
            self.employee_id.write({'nurse': self.service_nurse})

        if self.service_speciality != self.employee_id.seciality:
            self.employee_id.write({'seciality': self.service_speciality})

        if self.service_birthday !=  self.employee_id.birthday:
            self.employee_id.write({'birthday': self.service_birthday})
            
        self.employee_id.write({'state': 'approved'})

        return self.write({'state': 'approved',
                           'service_status': 'Approved'})


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for record in self:
            employee = record.employee_id

            # data header
            record.emp_id = employee.employee_id
            record.nik = employee.nik
            record.nik_lama = employee.nik_lama
            record.area = employee.area
            record.branch_id = employee.branch_id
            record.directorate_id = employee.directorate_id
            record.hrms_department_id = employee.hrms_department_id or False
            record.division_id = employee.division_id
            record.job_id = employee.job_id
            record.parent_id = employee.parent_id
            record.work_unit = employee.work_unit
            record.employee_group1s = employee.employee_group1s.id
            record.parent_nik = employee.parent_id.nik
            record.medic = employee.medic
            record.nurse = employee.nurse
            record.speciality = employee.seciality

            # data detail
            record.service_nik = str(str(employee.nik).replace("('", '')).replace("')", "")
            record.service_nik_lama = str(str(employee.nik_lama).replace("('", '')).replace("')", "")
            record.nik_lama = record.service_nik_lama
            record.service_name = employee.name
            record.service_previous_name = employee.name
            # record.service_area = employee.area.id
            # record.service_bisnisunit = employee.hrms_department_id.branch_id.id or employee.branch_id.id
            # record.service_directorate_id = employee.directorate_id.id
            # record.service_departmentid = employee.hrms_department_id.id
            # record.service_division_id = employee.division_id.id
            # record.service_jobtitle = employee.job_id.id
            # record.service_jobstatus = employee.job_status
            record.service_medic = employee.medic.id
            record.service_nurse = employee.nurse.id
            record.service_speciality = employee.seciality.id
            record.service_employementstatus = 'confirmed'
            record.service_employee_levels = employee.employee_levels.id
            record.service_empgroup1 = employee.employee_group1
            record.service_no_npwp = employee.no_npwp
            record.service_no_ktp = employee.no_ktp
            record.employee_levels = employee.employee_levels.id
            record.join_date = employee.join_date
            record.marital = employee.marital
            record.service_birthday = employee.birthday

            record.service_status = 'Draft'


    # def button_intransfer(self):
    #     self.write({'state': 'intransfer'})
    #     return True

    # def button_accept(self):
    #     self.write({'state': 'accept'})
    #     return True
    
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

