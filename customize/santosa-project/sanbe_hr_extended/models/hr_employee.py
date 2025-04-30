# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
import pytz
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from datetime import date

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
    branch_id = fields.Many2one('res.branch', string='Business Unit', domain="[('id','in',branch_ids)]", tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    medic = fields.Many2one('hr.profesion.medic', 'Profesi Medis',tracking=True, )
    nurse = fields.Many2one('hr.profesion.nurse', 'Profesi Perawat',tracking=True, )
    seciality = fields.Many2one('hr.profesion.special', 'Kategori Khusus',tracking=True, )
    street = fields.Char(related='branch_id.street')
    street2 = fields.Char(related='branch_id.street2')
    city = fields.Char(related='branch_id.city')
    state_id = fields.Char(related='branch_id.state_id')
    zip = fields.Char(related='branch_id.zip')
    country_id = fields.Many2one(related='branch_id.country_id')
    department_id = fields.Many2one('hr.department', compute = '_find_department_id',  string='Departemen', store=True, required=False)
    hrms_department_id = fields.Many2one('sanhrms.department', tracking=True, string='Departemen')
    
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
    nik = fields.Char('NIK')
    nik_lama = fields.Char('NIK Lama')
    no_ktp = fields.Char('No KTP')
    spk = fields.Char('No. SPK',store=True)
    spk_start = fields.Date('SPK Date',store=True)
    spk_finish = fields.Date('SPK Finish',store=True)
    skills_ids = fields.Many2many('hr.skill','hr_skills_emp_rel')
    doc_ktp = fields.Many2many('ir.attachment', 'hr_employee_rel', string='KTP Document',
                               help="You may attach files to with this")
    no_npwp = fields.Char('No NPWP')
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

    join_date = fields.Date('Join Date',tracking=True, )
    job_status_id = fields.Many2one('sanhrms.job.status',required=True, string='Status Pekerjaan')
    job_status_type = fields.Selection(related='job_status_id.type',store=True)
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], default='contract', tracking=True, string='Status Hubungan Kerja')
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('transfer_to_group', 'Transfer To Group'),
                                   ('terminated', 'Terminated'),
                                   ('pass_away', 'Pass Away'),
                                   ('long_illness', 'Long Illness')
                                   ], tracking=True, string='Employment Status')
    ws_month = fields.Integer('Working Service Month', compute="_compute_service_duration_display", readonly=True)
    ws_year = fields.Integer('Working Service Year', compute="_compute_service_duration_display", readonly=True)
    ws_day = fields.Integer('Working Service Day', compute="_compute_service_duration_display", readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', index=True)
    contract_datefrom = fields.Date('Contract Date From', related='contract_id.date_start', tracking=True,  store=True)
    contract_dateto = fields.Date('Contract Date To', related='contract_id.date_end', tracking=True, store=True)
    attachment_contract = fields.Binary(string='Contract Document', attachment=True)
    employee_group1s = fields.Many2one('emp.group',
                                       string='Employee P Group')
    employee_group1 = fields.Selection(selection=_selection1,
                                       default='Group2',
                                       string='Employee P Group')
    employee_levels = fields.Many2one('employee.level', string='Employee Level', index=True, store=True)
    insurance = fields.Char('BPJS No')
    jamsostek = fields.Char('Jamsostek')
    ptkp = fields.Char('PTKP')
    back_title = fields.Char('Back Title')
    no_sim = fields.Char('Driving Lisence #')
    attende_premie = fields.Boolean('Premi Kehadiran', default=False)
    attende_premie_amount = fields.Float(digits='Product Price', string='Jumlah Premi Kehadiran')
    allowance_jemputan = fields.Boolean('Jemputan')
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
    initial = fields.Char('Inisial')
    marital = fields.Selection([('single', 'Single'),
                            ('married', 'Married'),
                            ('seperate', 'Seperate')], string='Status Pernikahan')
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
    kontrak_medis = fields.Boolean(string="Kontrak Medis")
    sip_number = fields.Char(string="Nomor SIP")
    sip_date_from = fields.Date(string="Masa Berlaku SIP Dari")
    sip_date_to = fields.Date(string="Masa Berlaku SIP Hingga")
    competence = fields.Text(string="Kompetensi")

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

    _sql_constraints = [
        ('nik_uniq', 'check(1=1)', "The NIK  must be unique, this one is already assigned to another employee."),
        ('no_ktp_uniq', 'check(1=1)', "The NO KTP  must be unique, this one is already assigned to another employee."),
        ('no_npwp_uniq', 'check(1=1)',
         "The NO NPWP  must be unique, this one is already assigned to another employee."),
        ('identification_id_uniq', 'check(1=1)',
         "The Identification ID  must be unique, this one is already assigned to another employee."),
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
