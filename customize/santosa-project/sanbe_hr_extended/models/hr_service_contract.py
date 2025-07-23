from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo import fields, models, api

class ServiceContract(models.Model):
    _name = 'hr.service.contract'
    _description = 'Service Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    medical_contract_number = fields.Char(string='Nomor Kontrak Medis')
    contract_type_id = fields.Many2one('hr.contract.type', "Tipe Kontrak", tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                           string='Nama Karyawan',
                                           #domain="[('state','not in',['hold']),('job_status','=','contract')]",
                                           store=True,
                                           tracking=True)
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
    mc_number = fields.Selection([('1','1'),
                                ('2','2'),
                                ('3','3'),
                                ('4','4'),
                                ('5','5')],
                                string='Nomor Kontrak Medis Ke',
                                store=True)    
    start_date = fields.Date(string='Masa Berlaku Kontrak Medis Dari', required=True)
    end_date = fields.Date(string='Masa Berlaku Kontrak Medis Hingga', required=True)
    company_id = fields.Many2one(comodel_name='res.company', 
                                 store=True, readonly=False,
                                 default=lambda self: self.env.company, required=True)
    kd_day = fields.Integer(string='Hari Kontrak Medis', compute='_compute_kontrak_dinas', readonly=True)
    kd_month = fields.Integer(string='Bulan Kontrak Medis', compute='_compute_kontrak_dinas', readonly=True)
    kd_year = fields.Integer(string='Tahun Kontrak Medis', compute='_compute_kontrak_dinas', readonly=True)
    contract_counts = fields.Integer(string='Jumlah Kontrak Medis')
    attachment_contract =  fields.Many2many('ir.attachment',
                                            string='Dokumen Kontrak Medis',
                                            help="Lampirkan berkas disini")
    notice_day = fields.Integer(string='Periode Notifikasi')
    structure_type_id = fields.Many2one('hr.payroll.structure.type',
                                        string="Salary Structure Type",
                                        related='employee_id.contract_id.structure_type_id',
                                        store=True,
                                        readonly=False,
                                        tracking=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True, store=True)
    salary_amount = fields.Monetary(string='Jumlah Gaji', currency_field='currency_id')
    notes = fields.Text(string='Catatan')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], 
    string='Status', 
    tracking=True, 
    default="draft",
    help='Status Kontrak Medis'
    )
    kontrak_medis = fields.Boolean(related="employee_id.kontrak_medis", string="kontrak medis", store=True)
    competence = fields.Text(string="Kompetensi")

    
    def unlink(self):
        return super(ServiceContract, self).unlink()

    # kondisi kontrak medis bernilai False di tabsheet form employee
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        employee_id = self.env.context.get('default_employee_id')
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if not employee.kontrak_medis:
                raise UserError("Kontrak medis hanya bisa diisi jika flag kontrak medis bernilai True / dicentang.")
        return res
    
    # kondisi kontrak medis bernilai False di form kontrak medis
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if not employee.kontrak_medis:
                raise UserError("Kontrak medis hanya bisa diisi jika flag kontrak medis bernilai True / dicentang.")     
        return super().create(vals)

    
    # @api.onchange('state')
    # def onchange_field(self):
    #     for line in self:
    #         if line.state ==  'open':
    #             line.employee_id.kontrak_medis = True
    #             line.employee_id.kontrak_medis_id = line.id
    #             line.employee_id.sip_number = line.sip_number
    #             line.employee_id.sip_date_from = line.start_date
    #             line.employee_id.sip_date_to = line.end_date
    #         else:
    #             line.employee_id.kontrak_medis = False
    #             line.employee_id.kontrak_medis_id = False
    #             line.employee_id.sip_number = False
    #             line.employee_id.sip_date_from = False
    #             line.employee_id.sip_date_to = False


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

