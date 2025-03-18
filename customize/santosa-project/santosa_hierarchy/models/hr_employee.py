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

class HrEmployee(models.Model):
    """
    Extends the 'hr.employee' model to include additional fields related to
    employee resignation.
    """
    _inherit = 'hr.employee'

    # @api.depends('job_status')
    # def _get_domain_emp_status_id(self):
    #     print("kedua")
    #     for record in self:
    #         if record.job_status == 'contract':
    #             return [('id', '=', 1)]
    #         elif record.job_status == 'permanent':
    #             return [('id', 'in', [1, 2])]
    #         else:
    #             return []

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
    def _selection1(self):
        return EMP_GROUP1

    resign_date = fields.Date('Resign Date', readonly=True,
                              help="Date of the resignation")
    resigned = fields.Boolean(string="Resigned", default=False,
                              help="If checked then employee has resigned")
    fired = fields.Boolean(string="Fired", default=False,
                           help="If checked then employee has fired")
    birthday = fields.Date(string='Date of Birth', groups="base.group_user",
                           help="Birthday")
    branch_id = fields.Many2one('res.branch',string='Unit Bisnis')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Directorate')
    hrms_department_id = fields.Many2one('sanhrms.department',string='Department')
    division_id = fields.Many2one('sanhrms.division',string='Division')
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
        tracking=3,
        default='draft')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    alldepartment = fields.Many2many('hr.department', 'hr_department_rel', string='All Department',
                                     compute='_isi_department_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis', domain="[('id','in',branch_ids)]", tracking=True,
                                required=True)
    
    gender = fields.Selection([
        ('male', 'Laki-laki'),
        ('female', 'Perempuan'),
        ('other', 'Lainnya')
    ], groups="hr.group_hr_user", tracking=True, string="Jenis Kelamin")

    # street = fields.Char(related='branch_id.street')
    # street2 = fields.Char(related='branch_id.street2')
    # city = fields.Char(related='branch_id.city')
    # state_id = fields.Char(related='branch_id.state_id')
    # zip = fields.Char(related='branch_id.zip')
    country_id = fields.Many2one('res.country', 'Kewarganegaraan', groups="hr.group_hr_user", tracking=True)
    # identification_id = fields.Char(string='Nomor Kartu Keluarga', groups="hr.group_hr_user", tracking=True)
    nomor_kk = fields.Char(string='Nomor Kartu Keluarga', groups="hr.group_hr_user", tracking=True)
    birthday = fields.Date('Tanggal Lahir', groups="hr.group_hr_user", tracking=True)
    place_of_birth = fields.Char('Tempat Lahir', groups="hr.group_hr_user", tracking=True)
    country_of_birth = fields.Many2one('res.country', string="Negara", groups="hr.group_hr_user", tracking=True)
    department_id = fields.Many2one(required=True, string='Department')
    employee_id = fields.Char('Employee ID', default='New')
    nik = fields.Char('NIK')
    nik_lama = fields.Char('NIK LAMA')
    no_ktp = fields.Char('NO KTP')
    doc_ktp = fields.Many2many('ir.attachment', 'hr_employee_rel', string='Lampiran KTP',
                               help="You may attach files to with this")
    no_npwp = fields.Char('No NPWP')
    doc_npwp = fields.Many2many('ir.attachment', 'hr_employee_rel', string='Lampiran NPWP',
                                help="You may attach files to with this")
    title = fields.Char('Title')
    license = fields.Char('License')
    religion = fields.Selection([('islam', 'Islam'),
                                 ('katolik', 'Katolik'),
                                 ('protestan', 'Protestan'),
                                 ('hindu', 'Hindu'),
                                 ('budha', 'Budha')],
                                default='islam', string='Agama')
    join_date = fields.Date('Tanggal Bergabung')
    job_status = fields.Selection([('permanent', 'PKWTT'),
                                   ('contract', 'PKWT'),
                                   ('kk_pkwt', 'Kontrak Klinis PKWT'),
                                   ('kk_pkwtt', 'Kontrak Klinis PKWTT'),
                                   ('kontrak_medis_mitra', 'Kontrak Medis Mitra'),
                                   ],
                                  default='contract', string='Status Hubungan Kerja')
    emp_status = fields.Selection([('probation', 'Masa Percobaan'),
                                   ('confirmed', 'Terkonfirmasi Aktif'),
                                   ('end_contract', 'Kontrak berakhir'),
                                   ('resigned', 'Mengundurkan diri'),
                                #    ('retired', 'Retired'),
                                #    ('transfer_to_group', 'Transfer To Group'),
                                   ('terminated', 'PHK'),
                                   ('pass_away', 'Meninggal'),
                                   ('long_illness', 'Sakit berkepanjangan')
                                   ], string='Status Kekaryawanan')
    insurance = fields.Char('Nomor BPJS')
    jamsostek = fields.Char('Jamsostek')
    ptkp = fields.Char('PTKP')
    back_title = fields.Char('Back Title')
    no_sim = fields.Char('Nomor SIM #')
    attende_premie = fields.Boolean('Premi Kehadiran', default=False)
    attende_premie_amount = fields.Float(digits='Product Price', string='Amount')
    allowance_jemputan = fields.Boolean('Jemputan')
    allowance_ot = fields.Boolean('Lembur')
    allowance_transport = fields.Boolean('Transport')
    allowance_meal = fields.Boolean('Uang Makan')
    jemputan_remarks = fields.Char('Jemputan Remarks')
    ot_remarks = fields.Char('OT Remarks')
    transport_remarks = fields.Char('Transport Remarks')
    meal_remarks = fields.Char('Remarks')
    allowance_night_shift = fields.Boolean('Dinas Malam')
    allowance_nightshift_remarks = fields.Char('Allowance Night Shift Remarks')
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
    work_unit = fields.Char('Unit kerja')
    position_in_work_unit = fields.Char('Position in Work Unit')
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
    first_date_join = fields.Date('Tanggal Pertama bergabung')
    workingday = fields.Integer(string='Jumlah Hari kerja', help='Total Working Day in a Month', required=False)
    address_ids = fields.One2many('hr.employee.addresses', 'employee_id', auto_join=True, string='Asset Details')
    contract_id = fields.Many2one('hr.contract', string='Nomor Kontrak', index=True)
    contract_datefrom = fields.Date('Mulai Kontrak', related='contract_id.date_start', store=True)
    contract_dateto = fields.Date('Akhir Kontrak', related='contract_id.date_end', store=True)
    ws_month = fields.Integer('Working Service Month', compute="_compute_service_duration_display", readonly=True)
    ws_year = fields.Integer('Working Service Year', compute="_compute_service_duration_display", readonly=True)
    ws_day = fields.Integer('Working Service Day', compute="_compute_service_duration_display", readonly=True)
    employee_levels = fields.Many2one('employee.level', string='Level', index=True)
    employee_group1 = fields.Selection(selection=[('shbc','SHBC'),('sanbe','Sanbe')], string='Group Penggajian')
    attachment_contract = fields.Binary(string='Contract Document', attachment=True)
    family_info_ids = fields.One2many('hr.employee.family', 'employee_id', string='Family', help='Family Information')
    periode_probation = fields.Integer('Masa percobaan',readonly="job_status != 'permanent'")
    ext_probation = fields.Integer('Perpanjangan Percobaan',readonly="job_status != 'permanent'")
    confirm_probation = fields.Date('Tanggal Terkonfirmasi')
    retire_age = fields.Integer('Usia Pensiun')
    pension_date = fields.Date('Tanggal Pensiun')
    bond_service = fields.Boolean('Ikatan Dinas',default=False)
    service_from = fields.Date('Ikatan Dinas Mulai')
    service_to = fields.Date('Ikatan Dinas Hingga')
    is_pinalty = fields.Boolean('Pinalti',default=False)
    pinalty_bs = fields.Integer('Pinalti BS')
    pinalty_amount = fields.Monetary('Jumlah Pinalti')
    resign_notice = fields.Integer('Masa pengunduran diri')
    hourly_cost = fields.Monetary('Hourly Cost')
    asset_ids = fields.One2many('hr.employee.assets','employee_id',auto_join=True,string='Asset Details')
    education_ids = fields.One2many('employee.educations','employee_id',string='Educations List',auto_join=True)
    certificate_ids = fields.One2many('hr.employee.certification','employee_id',string='Certificate List',auto_join=True)
    joining_date = fields.Date(compute='_compute_joining_date',
                               string='Joining Date', store=True,
                               help="Employee joining date computed from the"
                                    " contract start date")
    servicelog_ids = fields.One2many('hr.employment.log','employee_id',auto_join=True,string='Employement List')


    # emp_status_id = fields.Many2one('hr.emp.status', string='Status Kekaryawanan', 
    #                                 domain=lambda self: self._get_domain_emp_status_id())
    # status = fields.Char(related='emp_status_id.status')
    

    @api.depends('contract_id')
    def _compute_joining_date(self):
        """Compute the joining date of the employee based on their contract
         information."""
        for employee in self:
            employee.joining_date = min(
                employee.contract_id.mapped('date_start')) \
                if employee.contract_id else False

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

    document_count = fields.Integer(compute='_compute_document_count',
                                    string='Documents',
                                    help='Count of documents.')

    def _compute_document_count(self):
        """Get count of documents."""
        for rec in self:
            rec.document_count = self.env[
                'hr.employee.document'].sudo().search_count(
                [('employee_ref_id', '=', rec.id)])
    
    def action_document_view(self):
        """ Opens a view to list all documents related to the current
         employee."""
        self.ensure_one()
        return {
            'name': _('Documents'),
            'domain': [('employee_ref_id', '=', self.id)],
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref_id': %s}" % self.id
        }

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

            if vals.get('contract_id'):
                contractid = vals.get('contract_id')
                existing = self.env['hr.employee'].sudo().search([('name', '=', vals.get('name'))])
            # else:
            #     print('ini kemari ', vals.get('name'))
            #     return super(HrEmployee,self).create(vals_list)
            if 'emp_status_id' in vals:
                emp_status_record = self.env['hr.emp.status'].search([('id', '=', vals['emp_status_id'])], limit=1)
                vals['emp_status'] = emp_status_record.emp_status if emp_status_record else False
                
        res = super(HrEmployee, self).create(vals_list)
        if existing:
            #     print('ini bener ',existing.name)
            mycontract = self.env['hr.contract'].browse(contractid)
            myemps = self.env['hr.employee'].sudo().browse(mycontract.employee_id.id)
            myemps.unlink()
            mycontract.write({'employee_id': res.id})
        
        return res