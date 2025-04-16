from odoo import fields, models, api, tools
from odoo.exceptions import UserError


EMP_PROFILE_STATE = [
    ('active', 'Active'),
    ('inactive', 'In Active'),
    ('hold', 'Hold')
]

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

TAX_METHOD1 = [
    ('nett', 'Nett'),
    ('gross', 'Gross'),
]


class SbEmployeeProfile(models.Model):
    _name = 'sb.employee.profile'
    _description = 'Employee Profile'


    @api.model
    def _selection1(self):
        return EMP_GROUP1

    employee_id = fields.Many2one("hr.employee", string="Employee")
    employee_group1 = fields.Selection(related="employee_id.employee_group1", store=True)  
    nik = fields.Char(related="employee_id.nik", string='NIK', store=True)
    nik_lama = fields.Char(related="employee_id.nik_lama", string='NIK LAMA', store=True)
    no_npwp = fields.Char(related="employee_id.no_npwp", string='NPWP', store=True)
    gender = fields.Selection(selection=[('male', 'Male'),
                               ('female', 'Female'),
                               ('other', 'Other')
                              ],string="Gender", related="employee_id.gender", store=True)
    area = fields.Many2one(related="employee_id.area", string='Area', index=True, store=True)
    branch_id = fields.Many2one(related="employee_id.branch_id", string='Business Unit', index=True, store=True)
    department_id = fields.Many2one(related="employee_id.department_id", string='Sub Department', store=True)
    job_id = fields.Many2one(related="employee_id.job_id", string="Job Position", store=True)
    job_status = fields.Selection([('permanent', 'Permanent'),
                                   ('contract', 'Contract'),
                                   ('outsource', 'Outsource'),
                                   ('visitor', 'Visitor'),
                                   ('mitra', 'Mitra'),
                                   ('tka', 'TKA'),
                                   ],related="employee_id.job_status", store=True)
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('transfer_to_group', 'Transfer To Group'),
                                   ('terminated', 'Terminated'),
                                   ('pass_away', 'Pass Away'),
                                   ('long_illness', 'Long Illness')
                                   ], string='Employment Status', related="employee_id.emp_status", store=True)
    
    state = fields.Selection(selection=EMP_PROFILE_STATE, string="status")
    


    # employement details
    pay_type = fields.Selection(
        string='Pay Type',
        selection=[('monthly', 'Monthly'),
                   ('daily', 'Daily'), ],
        required=False)
    pay_period = fields.Selection(
        string='Pay Period',
        selection=[('monthly', 'Monthly'),
                   ('daily', 'Daily'), ],
        required=False)
    effective_date = fields.Date(string='Effective Date', required=False)
    bank_account = fields.Char(string='Bank Account', required=False)
    basic_salary = fields.Float(string='Basic Salary', required=False)
    status_ptkp = fields.Selection(
        string='Status PTKP',
        selection=[('tk0', 'TKO'),
                   ('tk1', 'TK1')],
        required=False)
    type_ter = fields.Selection(
        string='Type TER',
        selection=[('tera', 'TER A'),
                   ('terb', 'TER B')],
        required=False)
    tax_method = fields.Selection(selection=TAX_METHOD1, string="Tax Method", index=True, default="nett")
    bpjs_no = fields.Char(string='BPJS No', required=False)
    jamsostek_no = fields.Char(string='Jamsostek No', required=False)
    # end employement details
    compensation_ids = fields.One2many(
        comodel_name='sb.compensation',
        inverse_name='compensation_id',
        string='Compensation Details',
        required=False)
    
    # allowance and deduction fields
    pay_code = fields.Selection(string='Pay Code',
                                selection=[('trans', 'TRANS'),
                                           ('cash', 'CASH')], 
                                required=False)
    amount = fields.Float(string='Amount', required=False)
    times = fields.Float(string='Times')
    pct_from_bs = fields.Float(string="from BS")
    formula = fields.Char(string='Formula')
    start_date = fields.Date(string='Start date')
    taxed = fields.Boolean(string="Tax")
    remarks = fields.Char(string="Remarks")
    allowance_ids = fields.One2many(comodel_name="allowance.deduction.detail", 
                                    inverse_name="allowance_id", 
                                    string="Allowance Id")

    selected_detail_id = fields.Many2one(
    comodel_name='allowance.deduction.detail', 
    string="Selected Detail", 
    ondelete="set null",
    help="Menyimpan ID detail yang sedang diedit"
    )


    @api.model
    def create_employee_profiles(self):
        employees = self.env['hr.employee'].search([('emp_status', '=', 'confirmed')])

        for employee in employees:
            if not self.search([('employee_id', '=', employee.id)]):
                self.create({'employee_id': employee.id})

    def init(self):
        self.create_employee_profiles()


    def btn_active(self):
        for rec in self:
            rec.state = 'active'
    
    def btn_inactive(self):
        for rec in self:
            rec.state = 'inactive'

    def btn_hold(self):
        for rec in self:
            rec.state = 'hold'


    def unlink(self):
        return super(SbEmployeeProfile, self).unlink()
        
    def btn_save(self):
        # Pastikan hanya satu record yang diproses
        self.ensure_one()

        if self.selected_detail_id:
            self.selected_detail_id.sudo().write({
                'pay_code': self.pay_code,
                'amount': self.amount, 
                'times': self.times,
                'remarks': self.remarks,
                'formula': self.formula,
                'pct_from_bs': self.pct_from_bs,
                'start_date': self.start_date,
            })
        else:
            # Jika tidak ada yang sedang diedit, buat baru
            new_detail = self.env['allowance.deduction.detail'].sudo().create({
                'allowance_id': self.id,
                'pay_code': self.pay_code,
                'amount': self.amount, 
                'times': self.times,
                'remarks': self.remarks,
                'formula': self.formula,
                'pct_from_bs': self.pct_from_bs,
                'start_date': self.start_date,
                })
            self.selected_detail_id = new_detail

        # Kosongkan input di header setelah save    
        self.pay_code = False
        self.amount = False
        self.times = False
        self.remarks = False
        self.formula = False
        self.pct_from_bs = False
        self.start_date =  False
        self.selected_detail_id = False


    def action_view_employee_profile_details(self):
        pass
        # return {
        #     'name': 'action_view_tms_details',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'sb.tms.tmsentry.details',
        #     'views': [(False, 'form')],
        #     'view_id': False,
        #     'view_id': self.env.ref('sanbe_hr_tms.tmsentry_details_form_view').id,
        #     'target': 'new',
        #     'res_id': self.id,
        #     'context': False,
        # }


class AllowanceDeductionDetail(models.Model):
    _name = 'allowance.deduction.detail'
    _description = 'Allowance Deduction Detail'


    allowance_id = fields.Many2one(
        comodel_name="sb.employee.profile", 
        string="Allowance and Deduction ID",
        ondelete="cascade", 
        index=True
    ) 
    pay_code = fields.Selection(string='Pay Code',
                                selection=[('trans', 'TRANS'),
                                           ('cash', 'CASH')], 
                                required=False)
    # pay_group = fields.Char(string="Pay Group")
    # pay_type = fields.Selection(related="allowance_id.pay_type", string="Pay Type", readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    formula = fields.Char(string='Formula', readonly=True)
    times = fields.Float(string='Times', readonly=True)
    start_date = fields.Date(string='Start date')
    taxed = fields.Boolean(string="Tax")
    remarks = fields.Char(string="Remarks", readonly=True)
    pct_from_bs = fields.Float(string="% from BS")


    def btn_edit(self):
        for record in self:
            if record.allowance_id:
                record.allowance_id.write({
                    'selected_detail_id': record.id,  # Simpan ID yang sedang diedit
                    'pay_code': self.pay_code,
                    'amount': self.amount, 
                    'times': self.times,
                    'remarks': self.remarks,
                    'formula': self.formula,
                    'pct_from_bs': self.pct_from_bs,
                    'start_date': self.start_date,
                })