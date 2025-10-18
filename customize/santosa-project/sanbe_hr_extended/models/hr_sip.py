from odoo import fields, models, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class SuratIzipPraktek(models.Model):
    _name = 'hr.sip'
    _description = 'Surat Izin Praktek'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    sip_number = fields.Char(string='Nomor SIP / Sertipikasi', required=True, tracking=True)
    contract_type_id = fields.Many2one('hr.contract.type', "Tipe Kontrak", tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Nama Karyawan', tracking=True)
    emp_selected_id = fields.Char(
        related='employee_id.employee_id',
        string='ID Karyawan',
        tracking=True,
        store=True,
        index=True
    )
    nik = fields.Char(string='NIK', related='employee_id.nik', store=True)
    nik_lama = fields.Char(string='NIK Lama', related='employee_id.nik_lama', store=True)
    area = fields.Many2one(related='employee_id.area', string='Area', store=True)
    department_id = fields.Many2one(related='employee_id.department_id', store=True, string='Departemen')
    hrms_department_id = fields.Many2one(related='employee_id.hrms_department_id', store=True, string='Departemen')
    directorate_id = fields.Many2one(related='employee_id.directorate_id', string='Direktorat', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    branch_id = fields.Many2one(related='employee_id.branch_id', string='Unit Bisnis', store=True)
    job_id = fields.Many2one(related='employee_id.job_id', string='Jabatan', store=True)
    sip = fields.Boolean(related='employee_id.sip', string='SIP', store=True)
    competence = fields.Text(string="Kompetensi")
    start_date = fields.Date(string='Masa Berlaku SIP Dari', required=True)
    end_date = fields.Date(string='Masa Berlaku SIP Hingga', required=True)
    no_sip_to = fields.Selection(
        selection=[
            ('1','1'),
            ('2','2'),
            ('3','3'),
            ('4','4'),
        ],
        string='Nomor SIP ke',
        store=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    sip_day = fields.Integer(string='Hari Kontrak Medis', compute='_compute_sip_date')
    sip_month = fields.Integer(string='Bulan Kontrak Medis', compute='_compute_sip_date')
    sip_year = fields.Integer(string='Tahun Kontrak Medis', compute='_compute_sip_date')
    contract_counts = fields.Integer(string='Jumlah SIP')
    attachment_contract =  fields.Many2many('ir.attachment',
                                            string='Dokumen SIP',
                                            help="Lampirkan file disini")
    notice_day = fields.Integer(string='Periode Notifikasi')
    structure_type_id = fields.Many2one('hr.payroll.structure.type',
                                        string="Salary Structure Type",
                                        related='employee_id.contract_id.structure_type_id',
                                        store=True,
                                        readonly=False,
                                        tracking=True)
    currency_id = fields.Many2one(related='company_id.currency_id', string="Currency", store=True)
    salary_amount = fields.Monetary(string='Jumlah Gaji', currency_field='currency_id')
    notes = fields.Text(string='Catatan')
    state = fields.Selection(
        selection=[
            ('draft', 'New'),
            ('open', 'Running'),
            ('close', 'Expired'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        tracking=True,
        default='draft',
        help='Status Surat Izin Praktek'
    )
    specialization = fields.Char(string='Spesialisasi')
    professional_title = fields.Char(string='Gelar Profesi')
    practice_day = fields.Char(string='Hari Praktek')
    work_start = fields.Float(string='Jam Kerja dari')
    work_end = fields.Float(string='Jam Kerja ke')


    def unlink_sip(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Data hanya bisa dihapus jika status SIP adalah 'New'.")
        
        return super().unlink()


    # kondisi sip bernilai false di tabsheet sip
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        employee_id = self.env.context.get('default_employee_id')

        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if not employee.sip:
                raise UserError('Surat Izin Praktek hanya bisa diisi jika flag sip bernilai True / dicentang.')
        
        return res


    @api.depends('start_date', 'end_date')
    def _compute_sip_date(self):
        for record in self:
            if record.start_date and record.end_date:
                duration_until = record.end_date
                if record.start_date and duration_until > record.start_date:

                    sip_duration = relativedelta(duration_until, record.start_date)
                    
                    record.sip_year = sip_duration.years
                    record.sip_month = sip_duration.months
                    record.sip_day = sip_duration.days
                else:
                    record.sip_year = 0
                    record.sip_month = 0
                    record.sip_day = 0
            else:
                record.sip_year = 0
                record.sip_month = 0
                record.sip_day = 0








