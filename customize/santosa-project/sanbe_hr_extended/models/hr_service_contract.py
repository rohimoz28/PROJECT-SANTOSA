from dateutil.relativedelta import relativedelta
from odoo import fields, models, api

class ServiceContract(models.Model):
    _name = 'hr.service.contract'
    _description = 'Service Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    sip_number = fields.Char(string='Nomor SIP')
    contract_type_id = fields.Many2one('hr.contract.type', "Tipe Kontrak", tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', 
                                  string='ID Karyawan', 
                                  readonly=True,
                                  tracking=True, 
                                  domain="[('state','not in',['hold']),('job_status','=','contract')]", 
                                  store=True,
                                  index=True)
    emp_name_selectec_id = fields.Many2one(comodel_name='hr.employee',
                                           string='Nama Karyawan',
                                           domain="[('state','not in',['hold']),('job_status','=','contract')]")
    nik = fields.Char(string='NIK')
    nik_lama = fields.Char(string='NIK Lama')
    area = fields.Many2one(comodel_name='res.territory', 
                           string='Area', 
                           tracking=True, 
                           store=True,
                           required=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id')
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id')
    branch_id = fields.Many2one(related='employee_id.branch_id', store=True, string="Unit Bisnis")
    department_id = fields.Many2one('hr.department', 
                                    compute='_find_department_id', 
                                    string='Departemen', 
                                    store=True, related='employee_id.department_id')
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id')
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
    start_date = fields.Date(string='Tanggal Mulai')
    end_date = fields.Date(string='Tanggal Berakhir')
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
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    salary_amount = fields.Monetary(string='Jumlah Gaji', currency_field='currency_id')
    notes = fields.Html(string='Catatan')

    # contract_id = fields.Many2one(comodel_name='hr.contract',
    #                               string='Contract',
    #                               domain="[('employee_id', '=', employee_id)]")
    state = fields.Selection([
        # related='contract_id.state',
        # string='Kontrak Status',
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Status', tracking=True, help='Status Kontak Dinas'
    )

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

    @api.depends('employee_id')
    def _compute_employee_contract(self):
        for contract in self.filtered('employee_id'):
            contract.job_id = contract.employee_id.job_id
            contract.department_id = contract.employee_id.department_id
            contract.company_id = contract.employee_id.company_id
            contract.area = contract.employee_id.area.id
            contract.branch_id = contract.employee_id.branch_id.id
            contract.nik = contract.employee_id.nik
            contract.nik_lama = contract.employee_id.nik_lama    


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

    @api.onchange('emp_name_selectec_id')
    def _onchange_emp_name_selectec_id(self):
        for rec in self:
            if rec.emp_name_selectec_id:
                rec.employee_id = rec.emp_name_selectec_id
