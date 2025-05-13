from dateutil.relativedelta import relativedelta
from odoo import fields, models, api

class ServiceContract(models.Model):
    _name = 'hr.service.contract'
    _description = 'Service Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    sip_number = fields.Char(string='Nomor SIP')
    contract_type_id = fields.Many2one('hr.contract.type', "Tipe Kontrak", tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                           string='Nama Karyawan',
                                           #domain="[('state','not in',['hold']),('job_status','=','contract')]",
                                           store=True)
    emp_selected_id = fields.Char(related='employee_id.employee_id', 
                                  string='ID Karyawan', 
                                  readonly=True,
                                  tracking=True, 
                                  store=True,
                                  index=True)
    nik = fields.Char(string='NIK', related='employee_id.nik', store=True)
    nik_lama = fields.Char(string='NIK Lama', related='employee_id.nik_lama', store=True)
    area = fields.Many2one(related='employee_id.area', 
                           string='Area', 
                           tracking=True, 
                           store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    branch_id = fields.Many2one(related='employee_id.branch_id', store=True, string="Unit Bisnis")
    department_id = fields.Many2one('hr.department', 
                                    compute='_find_department_id', 
                                    string='Departemen', 
                                    store=True, related='employee_id.department_id')
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    alldepartment = fields.Many2many('hr.department',
                                     'hr_department_rel', 
                                     string='All Department',
                                     compute='_isi_department_branch',
                                     store=True)
    depart_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]",
                                string='Sub Department')
    job_id = fields.Many2one('hr.job',string='Jabatan', 
                             related='employee_id.job_id', readonly=True, store=True)
    no_pkwt = fields.Selection([('1','1'),
                                ('2','2'),
                                ('3','3'),
                                ('4','4'),
                                ('5','5')],
                                string='Nomor PKWT')    
    start_date = fields.Date(string='Tanggal Mulai', required=True)
    end_date = fields.Date(string='Tanggal Berakhir', required=True)
    company_id = fields.Many2one('res.company', compute='_compute_employee_contract', 
                                 store=True, readonly=False,
                                 default=lambda self: self.env.company, required=True)
    kd_day = fields.Integer(string='Hari Kontrak Dinas', compute='_compute_kontrak_dinas', readonly=True)
    kd_month = fields.Integer(string='Bulan Kontrak Dinas', compute='_compute_kontrak_dinas', readonly=True)
    kd_year = fields.Integer(string='Tahun Kontrak Dinas', compute='_compute_kontrak_dinas', readonly=True)
    contract_counts = fields.Integer(string='Jumlah Kontrak')
    attachment_contract =  fields.Many2many('ir.attachment',
                                            string='Dokumen Kontrak',
                                            help="You may attach files to with this")
    notice_day = fields.Integer(string='Periode Notifikasi')
    structure_type_id = fields.Many2one('hr.payroll.structure.type',
                                        string="Salary Structure Type",
                                        related='employee_id.contract_id.structure_type_id',
                                        store=True,
                                        readonly=False,
                                        tracking=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True, store=True)
    salary_amount = fields.Monetary(string='Jumlah Gaji', currency_field='currency_id')
    notes = fields.Html(string='Catatan')
    state = fields.Selection([
        # related='contract_id.state',
        # string='Kontrak Status',
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Status', tracking=True, help='Status Kontak Dinas'
    )
    
    
    def unlink(self):
        return super(ServiceContract, self).unlink()
    
    @api.onchange('state')
    def onchange_field(self):
        for line in self:
            if line.state ==  'open':
                line.employee_id.kontrak_medis = True
                line.employee_id.kontrak_medis_id = line.id
                line.employee_id.sip_number = line.sip_number
                line.employee_id.sip_date_from = line.start_date
                line.employee_id.sip_date_to = line.end_date
            else:
                line.employee_id.kontrak_medis = False
                line.employee_id.kontrak_medis_id = False
                line.employee_id.sip_number = False
                line.employee_id.sip_date_from = False
                line.employee_id.sip_date_to = False


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


    @api.depends('start_date', 'end_date')
    def _compute_kontrak_dinas(self):
        for record in self:
            if record.start_date and record.end_date:
                service_until = record.end_date
                if record.start_date and service_until > record.start_date:
                    service_duration = relativedelta(
                        service_until, record.start_date
                    )
                    record.kd_year = service_duration.years
                    record.kd_month = service_duration.months
                    record.kd_day = service_duration.days
                else:
                    record.kd_year = 0
                    record.kd_month = 0
                    record.kd_day = 0
            else:
                    record.kd_year = 0
                    record.kd_month = 0
                    record.kd_day = 0

