from odoo import fields, models, tools, api, _


class HrEmployeeView(models.Model):
    _auto = False
    _name = 'hr.employee.view'
    _description = 'HR Employee View SQL'
    _order = 'name'

    id = fields.Integer(string='ID', required=True)
    name = fields.Char(string='Nama Karyawan')
    employee_id = fields.Char(string='ID Karyawan')
    nik = fields.Char(string='NIK')
    nik_lama = fields.Char(string='NIK Lama')
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
    employee_levels = fields.Many2one('employee.level', string='Employee Level')
    employee_group1s = fields.Many2one('emp.group', string='Employee P Group')
    medic = fields.Many2one('hr.profesion.medic', string='Profesi Medis')
    nurse = fields.Many2one('hr.profesion.nurse', string='Profesi Perawat')
    seciality = fields.Many2one('hr.profesion.special', string='Kategori Khusus')
    area_id = fields.Many2one('res.territory', string='Area')
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis')
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat')
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen')
    division_id = fields.Many2one('sanhrms.division', string='Divisi')
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], string='Status Hubungan Kerja')
    job_id = fields.Many2one('hr.job', string='Jabatan')
    parent_id = fields.Many2one('parent.hr.employee', string='Atasan Langsung')

    join_date = fields.Date(string='Join Date')
    marital = fields.Selection([('', ''),
                                ('single', 'Belum Menikah'),
                                ('married', 'Menikah'),
                                ('seperate', 'Berpisah')], string='Status Perkawinan')
    birthday = fields.Date(string='Tanggal Lahir')
    identification_id = fields.Char(string='Nomor Kartu Keluarga')
    no_npwp = fields.Char(string='Nomor NPWP')
    no_ktp = fields.Char(string='No KTP')
    work_unit = fields.Char('Unit Kerja')
    work_unit_id = fields.Many2one('hr.work.unit', string='Posisi Unit Kerja')
    coach_id = fields.Many2one('parent.hr.employee', tracking=True, string='Atasan Unit Kerja')
    # employee_category = fields.Selection(
    #     selection=[
    #         ('nakes', 'Nakes'),
    #         ('perawat', 'Perawat'),
    #         ('dokter', 'Dokter'),
    #         ('back_office', 'Back Office'),
    #     ],
    #     string='Kategori')

    state = fields.Selection([
        ('draft', "Draft"),
        ('req_approval', 'Request For Approval'),
        ('rejected', 'Rejected'),
        ('inactive', 'Inactive'),
        ('approved', 'Approved'),
        ('hold', 'Hold'),
    ], string="Status")
    active = fields.Boolean('Active')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    contract_datefrom = fields.Date('Contract From')
    contract_dateto = fields.Date('Contract To')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                select 
                    he.id as id, 
                    he.name as name,
                    he.employee_id,
                    he.nik,
                    he.nik_lama,
                    he.emp_status,
                    he.employee_levels,
                    he.employee_group1s,
                    he.medic,
                    he.nurse,
                    he.seciality,
                    he.area as area_id, 
                    he.branch_id,
                    he.directorate_id, 
                    he.hrms_department_id,
                    he.division_id,
                    he.job_status,
                    he.job_id,
                    he.parent_id,
                    he.join_date,
                    he.marital,
                    he.birthday,
                    he.identification_id,
                    he.no_npwp,
                    he.no_ktp,
                    he.work_unit,
                    he.work_unit_id,
                    he.coach_id,
                    he.contract_id,
                    he.contract_datefrom,
                    he.contract_dateto,
                    he.user_id,
                    he.state,
                    he.active
                from hr_employee he
            )
        """ % (self._table, ))

