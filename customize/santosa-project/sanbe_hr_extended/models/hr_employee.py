# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
import pytz
from odoo import api, fields, models, _, Command, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from datetime import date
from decimal import Decimal, ROUND_DOWN

import logging
_logger = logging.getLogger(__name__)

EMP_GROUP1 = [
    ('Group1', 'Group 1 - Harian(pak Deni)'),
    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
    ('Group4', 'Group 4 - Security and non apoteker (bu Susi)'),
    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
    ('Group7', 'Group 7 - Tim Proyek (pak Ferry)'),
]
EMP_GROUP2 = [
    ('Group1', 'Group 1 - Harian(pak Deni)'),
    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
    ('Group4', 'Group 4 - security(bu Susi)'),
    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
]
EMP_GROUP3 = [
    ('Group3', 'Group3 - Pusat')
]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id', '=', allrecs.branch_id.id)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]

    @api.model
    def _selection2(self):
        return EMP_GROUP2

    @api.model
    def _selection1(self):
        return EMP_GROUP1
        # else:
        #    return  EMP_GROUP1

    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    alldepartment = fields.Many2many('hr.department', 'hr_department_rel', string='All Department',
                                     compute='_isi_department_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='unit Bisnis', domain="[('id','in',branch_ids)]", tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    medic = fields.Many2one('hr.profesion.medic', 'Profesi Medis',tracking=True, )
    nurse = fields.Many2one('hr.profesion.nurse', 'Profesi Perawat',tracking=True, )
    seciality = fields.Many2one('hr.profesion.special', 'Kategori Khusus',tracking=True, )
    group_unit_id = fields.Many2one('mst.group.unit.pelayanan',tracking=True, )
    street = fields.Char(related='branch_id.street')
    street2 = fields.Char(related='branch_id.street2')
    city = fields.Char(related='branch_id.city')
    state_id = fields.Char(related='branch_id.state_id')
    zip = fields.Char(related='branch_id.zip')
    country_id = fields.Many2one(related='branch_id.country_id')
    department_id = fields.Many2one('hr.department', compute = '_find_department_id',  string='Old Departemen', store=True, required=False, Tracking=False)
    hrms_department_id = fields.Many2one('sanhrms.department', tracking=True, string='Departemen')
    medic_finish_date = fields.Date('SPK Date',store=True)
    
    @api.depends('hrms_department_id')
    def _find_department_id(self):
        for line in self:
            if line.hrms_department_id:
                Department = self.env['hr.department'].search([('name', 'ilike', line.division_id.name)], limit=1)
                if Department:
                    line.department_id = Department.id
                else:
                    Department = self.env['hr.department'].sudo().create({
                        'name': line.hrms_department_id.name,
                        'active': True,
                        'company_id': self.env.user.company_id.id,
                    })
                    line.department_id = Department.id
                     
    division_id = fields.Many2one('sanhrms.division', tracking=True, string='Divisi')
    directorate_id = fields.Many2one('sanhrms.directorate', tracking=True, string='Direktorat')
    employee_id = fields.Char('Employee ID', default='New')
    nik = fields.Char('NIK', index=True, tracking=True)
    nik_lama = fields.Char('NIK Lama')
    no_ktp = fields.Char('No KTP', tracking=True)
    spk = fields.Char('No. SPK', tracking=True, store=True)
    spk_start = fields.Date('SPK Date',store=True)
    spk_finish = fields.Date('SPK Finish',store=True)
    skills_ids = fields.Many2many('hr.skill','hr_skills_emp_rel')
    doc_ktp = fields.Many2many('ir.attachment', 'hr_employee_rel', string='KTP Document',
                               help="You may attach files to with this")
    no_npwp = fields.Char('No NPWP', tracking=True)
    doc_npwp = fields.Many2many('ir.attachment', 'hr_employee_rel', string='NPWP Document',
                                help="You may attach files to with this")
    title = fields.Char('Title')
    license = fields.Char('License')
    religion = fields.Selection([('islam', 'Islam'),
                                 ('katolik', 'Katolik'),
                                 ('protestan', 'Protestan'),
                                 ('hindu', 'Hindu'),
                                 ('budha', 'Budha')],
                                default='islam', string='Religion')
    join_date = fields.Date(string='Join Date', tracking=True)
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], default='contract', tracking=True, string='Status Hubungan Kerja', required=True)
    job_title = fields.Char(string='Job Title', compute='_compute_job_title',  store=True)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        self._compute_job_title()
    
    @api.depends('job_id')
    def _compute_job_title(self):
        for rec in self:
            rec.job_title = str(rec.job_id.display_name or '')
            
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('transfer_to_group', 'Transfer To Group'),
                                   ('terminated', 'Terminated'),
                                   ('pass_away', 'Pass Away'),
                                   ('long_illness', 'Long Illness')
                                   ], string='Employment Status')
    ws_month = fields.Integer('Working Service Month', compute="_compute_service_duration_display", readonly=True)
    ws_year = fields.Integer('Working Service Year', compute="_compute_service_duration_display", readonly=True)
    ws_day = fields.Integer('Working Service Day', compute="_compute_service_duration_display", readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', index=True, tracking=True)
    contract_datefrom = fields.Date('Contract Date From', related='contract_id.date_start', tracking=True,  store=True)
    contract_dateto = fields.Date('Contract Date To', related='contract_id.date_end', tracking=True, store=True)
    attachment_contract = fields.Binary(string='Contract Document', attachment=True)
    employee_group1s = fields.Many2one('emp.group', string='Employee P Group', tracking=True)
    employee_group1 = fields.Selection(selection=_selection1,
                                       default='Group2',
                                       string='Old Employee P Group')
    parent_id = fields.Many2one('parent.hr.employee', tracking=True, string='Atasan Langsung')
    coach_id = fields.Many2one('parent.hr.employee', tracking=True, string='Atasan Unit Kerja')
    coor_unit_id = fields.Many2one('parent.hr.employee', string='Atasan Unit Koordinasi', tracking=True)
    employee_levels = fields.Many2one('employee.level', string='Employee Level', index=True, store=True, tracking=True)
    insurance = fields.Char('BPJS No')
    jamsostek = fields.Char('Jamsostek')
    ptkp = fields.Char('PTKP')
    back_title = fields.Char('Back Title')
    no_sim = fields.Char('Driving Lisence #')
    attende_premie = fields.Boolean('Premi Kehadiran', default=False)
    attende_premie_amount = fields.Float(digits='Product Price', string='Jumlah Premi Kehadiran')
    allowance_jemputan = fields.Boolean('Jemputan')
    max_ot = fields.Float('Jam Lembur Maksimal', digits=(16, 1), default=0)
    
    @api.constrains('max_ot')
    def _check_max_ot(self):
        for rec in self:
            if rec.max_ot:
                if rec.max_ot <0:            
                    raise UserError("Values cannot be below zero")  
            value = Decimal(str(rec.max_ot))
            rounded = value.quantize(Decimal('0.1'), rounding=ROUND_DOWN)
            if value != rounded:
                raise UserError("Maximum of 1 digits allowed after decimal point.")
            if (value % Decimal('0.5')) != 0:
                raise UserError("Value must be a multiple of 0.5 Hours")
    
    allowance_ot = fields.Boolean('OT')
    allowance_transport = fields.Boolean('Transport')
    allowance_meal = fields.Boolean('Uang Makan')
    jemputan_remarks = fields.Char('Keterangan Penjemputan')
    ot_remarks = fields.Char('Keterangan Lembur')
    transport_remarks = fields.Char('Keterangan Transport')
    meal_remarks = fields.Char('Keterangan Makan')
    allowance_night_shift = fields.Boolean('Dinas Malam')
    allowance_nightshift_remarks = fields.Char('Keterangan Dinas Malam')
    allowance_nightshift_amount = fields.Float('Jumlah Premi Dinas Malam')
    state = fields.Selection([
        ('draft', "Draft"),
        ('req_approval', 'Request For Approval'),
        ('rejected', 'Rejected'),
        ('inactive', 'Inactive'),
        ('approved', 'Approved'),
        ('hold', 'Hold'),
    ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    nama_pekerjaans = fields.Char(related='job_id.name', store=True)
    gender_selection = fields.Selection([('male', 'Laki-Laki'),
                            ('female', 'Perempuan'),],compute="_get_gender_status",
                            inverse='onchange_gender_selection', string='Jenis Kelamin')
    marital = fields.Selection([('single', 'Single'),
                            ('married', 'Married'),
                            ('seperate', 'Seperate')], string='Status Pernikahan', default=False)
    
    marital_status = fields.Selection([('single', 'Belum Menikah'),
                            ('married', 'Menikah'),
                            ('seperate', 'Bercerai')],compute="_get_marital_status",
                            inverse='onchange_marital_status',
                             string='Status Perkawinan')

    
    @api.onchange('marital_status')        
    def onchange_marital_status(self):
        self.marital = self.marital_status
    
    @api.depends('marital')    
    def _get_marital_status(self):
        self.marital_status = self.marital

    @api.onchange('gender_selection')    
    def onchange_gender_selection(self):
        self.gender = self.gender_selection
    
    @api.depends('gender')    
    def _get_gender_status(self):
        self.gender_selection = self.gender
    
    work_unit = fields.Char('Work Unit')
    work_unit_id = fields.Many2one('hr.work.unit','Work Unit',tracking=True, )
    berat_badan = fields.Integer('Berat Badan (Kg)')
    tinggi_badan = fields.Integer('Tinggi Badan (Cm)')
    kpi_kategory = fields.Selection([('direct_spv', "Direct"),
                                     ('direct_lvp', 'Direct LVP'),
                                     ('direct_svp', 'Direct SVP'),
                                     ('indirect', 'Indirect'),
                                     ('general', 'General'),
                                     ('management', 'Management'),
                                     ('none', 'None')],
                                    string="KPI Category", index=True, tracking=True, default='none')
    apoteker = fields.Boolean('Apoteker', default=False)
    first_date_join = fields.Date('First Date Of Joining')
    workingday = fields.Integer(
        string='Jumlah Hari kerja',
        help='Jumlah Hari Kerja Dalam Satu Bulan',
        required=False)
    kontrak_medis = fields.Boolean(string="Kontrak Medis", tracking=True)
    
    @api.constrains('no_ktp','no_sim','no_npwp','identification_id')
    def _check_numeric_reference(self):
        for record in self:
            if record.no_ktp and not record.no_ktp.isdigit() :
                raise UserError("No. KTP harus Numerik.")
            if record.no_npwp and not record.no_npwp.isdigit() :
                raise UserError("No. NPWP harus Numerik")
            if record.no_sim and not record.no_sim.isdigit() :
                raise UserError("No. SIM harus Numerik")
            if record.identification_id and not record.identification_id.isdigit() :
                raise UserError("No. Kartu Keluarga harus Numerik")
            
    kontrak_medis_id = fields.Many2one('hr.service.contract')
    medical_contract_ids = fields.One2many(
        comodel_name='hr.service.contract',
        inverse_name='employee_id',
        string='Kontrak Medis',
    )
    sip = fields.Boolean(string="SIP", tracking=True)
    sip_ids = fields.One2many(
        comodel_name='hr.sip',
        inverse_name='employee_id',
        string='SIP'
    )
    employee_category = fields.Selection(
        selection=[
            ('nakes', 'Nakes'),
            ('perawat', 'Perawat'),
            ('dokter', 'Dokter'),
            ('back_office', 'Back Office'),
        ],
        string='Kategori',
    )


    # wage = fields.Monetary('Wage', required=True, tracking=True, help="Employee's monthly gross wage.", group_operator="avg")
    # contract_wage = fields.Monetary('Contract Wage', compute='_compute_contract_wage')
    # hra = fields.Monetary(string='HRA', tracking=True,
    #                       help="House rent allowance.")
    # travel_allowance = fields.Monetary(string="Travel Allowance",
    #                                    help="Travel allowance")
    # da = fields.Monetary(string="DA", help="Dearness allowance")
    # meal_allowance = fields.Monetary(string="Meal Allowance",
    #                                  help="Meal allowance")
    # medical_allowance = fields.Monetary(string="Medical Allowance",
    #                                     help="Medical allowance")
    # other_allowance = fields.Monetary(string="Other Allowance",
    #                                   help="Other allowances")

    #
    # @api.depends('wage')
    # def _compute_contract_wage(self):
    #     for contract in self:
    #         contract.contract_wage = contract._get_contract_wage()
    #
    # def _get_contract_wage(self):
    #     if not self:
    #         return 0
    #     self.ensure_one()
    #     return self[self._get_contract_wage_field()]
    #
    # def _get_contract_wage_field(self):
    #     self.ensure_one()
    #     return 'wage'
    
    # @api.depends("employee_skill_ids")

    _sql_constraints = [
        ('nik_uniq', 'unique(nik)', "The NIK  must be unique, this one is already assigned to another employee."),
        # ('no_ktp_uniq', 'unique(no_ktp)', "Nomor KTP sudah terdaftar di (SHBC/SHBK). Harap gunakan nomor unik."),
        # ('no_npwp_uniq', 'unique(no_npwp)', "Nomor NPWP sudah terdaftar di (SHBC/SHBK). Harap gunakan nomor unik."),
        # ('identification_id_uniq', 'unique(identification_id)', "The Identification ID  must be unique, this one is already assigned to another employee."),
    ]

    # @api.constrains('emp_status')
    # def _check_emp_status(self):
    #     for rec in self:
    #         if rec.state == 'draft' and rec.emp_status not in ['confirmed', 'probation']:
    #             raise UserError(_('New Employement only can selected Confirmed and Probation in Employement status'))

    # @api.onchange('emp_status')
    # def _onchange_emp_status(self):
    #     if self.emp_status not in ['probation', 'confirmed']:
    #         raise UserError(_('Only "Probation" or "Confirmed" can be selected for the Employment Status field.'))

    # def init(self):
    #    myemployee = self.env['hr.employee'].search([])
    #    for allemp in myemployee:
    #        if not allemp.nik_lama and allemp.nik:
    #            allemp.write({'nik_lama': allemp.nik})
    #    #myemployees = self.env['hr.employee'].search([])
    #    #for allemps in myemployees:
    #    #    allemps.write({'nik_lama': ''})

    @api.onchange('job_status')
    def _onchange_job_status(self):
        if self.job_status == 'partner_doctor':
            self.kontrak_medis = True
            self.sip = True
        else:
            self.kontrak_medis = False
            self.sip = False 

    @api.constrains('no_ktp', 'no_npwp', 'employee_category')
    def _check_unique_ktp_npwp(self):
        restricted_categories = ['nakes', 'perawat', 'back_office']

        for rec in self:
            # Dokter boleh duplikat
            if rec.employee_category == 'dokter':
                if rec.no_ktp:
                    conflict_ktp = self.env['hr.employee'].search_count([
                        ('id', '!=', rec.id),
                        ('no_ktp', '=', rec.no_ktp),
                        ('employee_category', '!=', 'dokter'),
                    ])
                    if conflict_ktp > 0:
                        raise ValidationError(_(
                            "Nomor KTP '%s' sudah digunakan oleh karyawan non-dokter di SHBC/SHBK. "
                            "Dokter hanya boleh menggunakan nomor miliknya sendiri."
                        ) % rec.no_ktp)

                if rec.no_npwp:
                    conflict_npwp = self.env['hr.employee'].search_count([
                        ('id', '!=', rec.id),
                        ('no_npwp', '=', rec.no_npwp),
                        ('employee_category', '!=', 'dokter'),
                    ])
                    if conflict_npwp > 0:
                        raise ValidationError(_(
                            "Nomor NPWP '%s' sudah digunakan oleh karyawan non-dokter di SHBC/SHBK. "
                            "Dokter hanya boleh menggunakan nomor miliknya sendiri."
                        ) % rec.no_npwp)
            else:
                # DUPE KTP
                if rec.no_ktp:
                    dup_ktp_count = self.env['hr.employee'].search_count([
                        ('id', '!=', rec.id),
                        ('no_ktp', '=', rec.no_ktp),
                    ])
                    if dup_ktp_count > 0:
                        raise ValidationError(_(
                            "Nomor KTP '%s' sudah digunakan oleh karyawan lain di SHBK/SHBC. "
                            "Harap gunakan nomor unik."
                        ) % rec.no_ktp)
                # DUPE NPWP
                if rec.no_npwp:    
                    dup_npwp_count = self.env['hr.employee'].search_count([
                        ('id', '!=', rec.id),
                        ('no_npwp', '=', rec.no_npwp),
                    ])
                    if dup_npwp_count > 0:
                        raise ValidationError(_(
                            "Nomor NPWP '%s' sudah digunakan oleh karyawan lain di SHBK/SHBC. "
                            "Harap gunakan nomor unik."
                        ) % rec.no_npwp)
                
    @api.model
    def default_get(self, default_fields):
        res = super(HrEmployee, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id': self.env.user.branch_id.id or False
            })
        return res

    #     myemployee = self.env['hr.employee'].search([])
    #     tmpnik = []
    #     tmponik =[]
    #     for semps in myemployee:
    #         semps.write({'nik_lama': allemp.nik})
    #         semps.env.cr.commit()
    #     for allemp in myemployee:
    #
    #         mycomp = self.env['res.company'].browse(allemp.company_id.id)
    #         dcomp = False
    #         bcode = False
    #         tgljoin = False
    #         jyear = False
    #         jmonth = False
    #
    #         if mycomp.name == "PT. Sanbe Farma":
    #             dcomp = '1'
    #             mybranch = self.env['res.branch'].sudo().browse(allemp.branch_id.id)
    #             if mybranch.branch_code == 'BU1':
    #                 bcode = '01'
    #             elif mybranch.branch_code == 'BU2':
    #                 bcode = '02'
    #             elif mybranch.branch_code == 'RND':
    #                 bcode = '03'
    #             elif mybranch.branch_code == 'CWH':
    #                 bcode = '04'
    #             elif mybranch.branch_code == 'BU3':
    #                 bcode = '05'
    #             elif mybranch.branch_code == 'BU4':
    #                 bcode = '06'
    #             elif mybranch.branch_code == 'BU5':
    #                 bcode = '07'
    #             elif mybranch.branch_code == 'BU6':
    #                 bcode = '08'
    #             elif mybranch.branch_code == 'SBE':
    #                 bcode = '09'
    #             elif mybranch.branch_code == 'CWC':
    #                 bcode = '10'
    #             if allemp.job_status =='permanent':
    #                 tgljoin = allemp.join_date
    #             else:
    #                 tgljoin= allemp.contract_datefrom
    #             if tgljoin:
    #                 jyear = tgljoin.strftime('%y')
    #                 jmonth =   tgljoin.strftime('%m')
    #                 nonik = '%s%s%s%s' %(dcomp,bcode,jyear,jmonth)
    #                 tmpnik.append({ 'tanggal': tgljoin,
    #                                 'nik': nonik,
    #                                 'empid': allemp.id})
    #                 allemp.write({'nik': nonik})
    #     awal = ''
    #
    #     for alltmp in tmpnik:
    #         myemp = self.env['hr.employee'].sudo().search([('nik','=',alltmp['nik'])])
    #         prefix = '00'
    #         cnt = 1
    #         urutan =1
    #         for allemps in myemp:
    #             niks = '%s' %(allemps.nik + prefix +str(urutan))
    #             urutan  = urutan +1
    #             allemps.write({'nik': niks})
    #             if  urutan >  10:
    #                 prefix = '0'
    #             elif urutan >100:
    #                 prefix =''

    # @api.constrains('no_npwp')
    # def _contrains_no_npwp(self):
    #     cekktp  = self.env['hr.employee'].sudo().search([('no_npwp','=', self.no_npwp)])
    #     if len(cekktp) > 1:
    #         raise UserError(_('A Employee with the same Nomor NPWP already exist.'))
    #
    # @api.constrains('identification_id')
    # def _contrains_identification_idp(self):
    #     cekktp  = self.env['hr.employee'].sudo().search([('identification_id','=', self.identification_id)])
    #     if len(cekktp) > 1:
    #         raise UserError(_('A Employee with the same Identification_id already exist.'))
    #
    # @api.constrains('no_ktp')
    # def _contrains_no_ktp(self):
    #     # Prevent a coupon from having the same code a program
    #     cekktp  = self.env['hr.employee'].sudo().search([('no_ktp','=', self.no_ktp)])
    #     if len(cekktp) > 1:
    #         raise UserError(_('A Employee with the same Nomor KTP already exist.'))

    # @api.constrains('nik')
    # def _contrains_nik(self):
    #     # Prevent a coupon from having the same code a program
    #     cekktp  = self.env['hr.employee'].sudo().search([('nik','=', self.nik)])
    #     if len(cekktp) > 1:
    #         raise UserError(_('A Employee with the same NIK already exist.'))

    @api.model
    def default_get(self, fields_list):
        res = super(HrEmployee, self).default_get(fields_list)
        if self.env.user.branch_id:
            res['area'] = self.env.user.area.id or False
            res['branch_id'] = self.env.user.branch_id.id or False
        return res

    @api.depends("join_date")
    def _compute_service_duration_display(self):
        for record in self:
            service_until = fields.Date.today()
            if record.join_date and service_until > record.join_date:
                service_duration = relativedelta(
                    service_until, record.join_date
                )
                record.ws_year = service_duration.years
                record.ws_month = service_duration.months
                record.ws_day = service_duration.days
            else:
                record.ws_year = 0
                record.ws_month = 0
                record.ws_day = 0

    @api.model
    def _cron_count_working_service(self, work_days=None):
        mysearch = self.env['hr.employee'].search([])
        for alldata in mysearch:
            if alldata.join_date:
                join_date = alldata.join_date
                current_date = fields.Date.today()
                service_duration = relativedelta(
                    current_date, join_date
                )
                dalamtahun = service_duration.years
                dalambulan = service_duration.months
                dalamhari = service_duration.days
                alldata.write({'ws_month': dalambulan, 'ws_year': dalamtahun, 'ws_day': dalamhari})
            else:
                alldata.write({'ws_month': 0, 'ws_year': 0})
        return True

    def write(self, vals):
        # for vals in vals_list:
        if vals.get('job_status'):
            if vals.get('job_status') == 'contract':
                vals['retire_age'] = 0
                vals['periode_probation'] = 0
                vals['joining_date'] = False

        if vals.get('nik'):
            gnik = vals.get('nik')
        else:
            gnik = self.nik

        if vals.get('badges_nos'):
            noss = vals.get('badges_nos')
            try:
                nos = noss[0][2][0]
            except:
                pass
                nos = noss[0][1]
            dat = self.env['hr.machine.details'].sudo().search([('id', '=', nos)], limit=1)
            if dat:
                dat.write({
                    'employee_id': self.id
                })

        if 'department_id' in vals:
            self = self.with_context(tracking_disable=True)    

        res = super(HrEmployee, self).write(vals)

        return res

    @api.model_create_multi
    def create(self, vals_list):
        contractid = False
        existing = False
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('employee_id', _("New")) == _("New"):
                vals['employee_id'] = self.env['ir.sequence'].next_by_code(
                    'hr.employee.sequence') or _("New")
            # if vals.get('nik', _("New")) == _("New"):
            #     mycomp = self.env['res.company'].browse(vals.get('company_id'))
            #     dcomp = False
            #     bcode = False
            #     if mycomp.name=="PT.Sanbe Farma":
            #         dcomp='1'
            #         mybranch = self.env['res.branch'].sudo().browse(vals.get('branch_id'))
            #         if mybranch.branch_code == 'BU1':
            #             bcode= '01'
            #         elif mybranch.branch_code == 'BU2':
            #             bcode= '02'
            #         elif mybranch.branch_code=='RND':
            #             bcode= '03'
            #         elif mybranch.branch_code=='CWH':
            #             bcode= '04'
            #         elif mybranch.branch_code== 'BU3':
            #             bcode= '05'
            #         elif mybranch.branch_code =='BU4':
            #             bcode= '06'
            #         elif mybranch.branch_code == 'BU5':
            #             bcode= '07'
            #         elif mybranch.branch_code =='BU6':
            #             bcode= '08'
            #         elif mybranch.branch_code =='SBE':
            #             bcode='09'
            #         elif mybranch.branch_code == 'CWC':
            #             bcode = 10

            if vals.get('job_status'):
                if vals.get('job_status') == 'contract':
                    vals['retire_age'] = 0
                    vals['periode_probation'] = 0
                    vals['joining_date'] = False
            
            res = super(HrEmployee, self).create(vals_list)
            if vals.get('contract_id'):
                contractid = vals.get('contract_id')
                existing = self.env['hr.employee'].sudo().search([('name', '=', vals.get('name'))])
                mycontract = self.env['hr.contract'].browse(contractid)
                mycontract.write({'employee_id': res.id})
            # else:
            #     print('ini kemari ', vals.get('name'))
            #     return super(HrEmployee,self).create(vals_list)
        
            if existing:
                #     print('ini bener ',existing.name)
                mycontract = self.env['hr.contract'].browse(contractid)
                myemps = self.env['hr.employee'].sudo().browse(mycontract.employee_id.id)
                myemps.unlink()
                mycontract.write({'employee_id': res.id})
            return res

    def unlink(self):
        for allrec in self:
            if allrec.state not in ['draft', 'req_approval']:
                raise UserError('Cannot Delete Employee not in draft')
        return super().unlink()

    @api.depends('name', "employee_id")
    def _compute_display_name(self):
        for account in self:
            myctx = self._context.get('search_by')
            sbn = self._context.get('search_by_name')
            if myctx and sbn == False:
                if myctx == 'No':
                    account.display_name = f"{account.employee_id}"
                else:
                    account.display_name = f"{account.name}"
            else:
                account.display_name = f"{account.name}"

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

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        parts = name.split('] ')
        if name:
            if len(parts) == 2:
                emp_id = parts[0][1:]
                emp_name = parts[1]
                name_domain = ['|',('employee_id', operator, emp_id), ('name', operator, emp_name)]
                return self._search(expression.AND([name_domain, domain]), limit=limit, order=order)
            else:
                name_domain = ['|',('employee_id', operator, name), ('name', operator, name)]
                return self._search(expression.AND([name_domain, domain]), limit=limit, order=order)
        return super()._name_search(name, domain, operator, limit, order)

    def _compute_hours_last_month(self):
        """
        Compute hours in the current month, if we are the 15th of october, will compute hours from 1 oct to 15 oct
        """
        now = fields.Datetime.now()
        now_utc = pytz.utc.localize(now)
        for employee in self:
            tz = pytz.timezone(employee.tz or 'UTC')
            now_tz = now_utc.astimezone(tz)
            start_tz = now_tz.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)
            end_tz = now_tz
            end_naive = end_tz.astimezone(pytz.utc).replace(tzinfo=None)

            hours = 0

            employee.hours_last_month = round(hours, 2)
            employee.hours_last_month_display = "%g" % employee.hours_last_month



class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    hr_employee_id = fields.Many2one('hr.employee', string='Employee ID')

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


class IrConfigParameter(models.Model):
    """Per-database storage of configuration key-value pairs."""
    _inherit = 'ir.config_parameter'

class ResUsers(models.Model):
    _inherit = "res.users"

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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            # mybranch = self.env['res.branch'].sudo().search([('branch_code','=','BU3')])
            mybranch = self.env.user.branch_id
            search_domain = [('name', operator, name), ('branch_id', '=', mybranch.id)]
            user_ids = self._search(search_domain, limit=1, order=order)
            return user_ids
        else:
            return super()._name_search(name, domain, operator, limit, order)

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


class ParentEmployee(models.Model):
    _name = 'parent.hr.employee'
    _description = 'Employee parent'
    _order = 'nik, name'
    _rec_name = 'display_name'
    _auto = False


    display_name = fields.Char(string='Cari', compute="_compute_display_name", store=True)
    id = fields.Many2one('hr.employee', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    name = fields.Char('Nama Karyawan', required=True)
    nik = fields.Char('NIK Karyawan', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis')
    directorate_id = fields.Many2one('sanhrms.directorate', tracking=True, string='Direktorat')
    division_id = fields.Many2one('sanhrms.division', tracking=True, string='Divisi')
    hrms_department_id = fields.Many2one('sanhrms.department', tracking=True, string='Departemen')
    job_id = fields.Many2one('hr.job', string='Jabatan', tracking=True)
    active = fields.Boolean()
    user_id = fields.Many2one('res.users')
    state = fields.Selection([
        ('draft', "Draft"),
        ('req_approval', 'Request For Approval'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('inactive', 'Inactive'),
        ('hold', 'Hold'),
    ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,store=True)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    id,
                    id AS employee_id,
                    name,
                    nik,
                    company_id,
                    branch_id,
                    active,
                    state,
                    job_id,
                    directorate_id,
                    hrms_department_id,
                    user_id,
                    division_id,
                    (nik || ' - ' || name) AS display_name  -- Tambahkan ini
                FROM hr_employee
            )
        """ % self._table)

        
    @api.depends('nik','name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = '%s - %s' % (account.nik   or '', account.name)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            return self.search([
                '|',
                ('nik', operator, name),
                ('name', operator, name)
            ] + args, limit=limit).name_get()
        return self.search(args, limit=limit).name_get()