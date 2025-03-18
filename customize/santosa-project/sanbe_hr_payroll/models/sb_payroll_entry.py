from odoo import fields, models, api


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

PAYROLL_SUMMARY_STATE = [
    ('draft', 'Draft'),
    ('approved', "Approved")
]

class SbPayrollEntry(models.Model):
    _name = 'sb.payroll.entry'
    _description = 'Payroll Entry'

    @api.model
    def _selection1(self):
        return EMP_GROUP1

    employee_group1 = fields.Selection(selection=_selection1, string='Employee P Group')
    employee_id = fields.Many2one('hr.employee', index=True)
    nik = fields.Char(
        string='NIK',
        required=False)
    period_pay_calc = fields.Date(
        string='Period Pay',
        required=False)
    calc_date = fields.Date(
        string='Calc Date',
        required=False)
    npwp = fields.Char(
        string='NPWP',
        required=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", tracking=True)
    emp_status = fields.Selection([('probation','Probation'),
                                   ('confirmed','Confirmed'),
                                   ('probation', 'Probation'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('terminated', 'Terminated'),
                                   ],string='Employment Status')
    job_id = fields.Many2one('hr.job', string='Job Position')
    bank_account = fields.Char(string='Bank Account')
    job_status = fields.Char(string='Job Status',required=False)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    state = fields.Selection(
        selection=PAYROLL_SUMMARY_STATE,
        string="Status",
        default='draft')
    detail_ids = fields.One2many(
        comodel_name='sb.payroll.entry.detail',
        inverse_name='master_id',
        string='Payroll Entry List',
        required=False)
    total_allowance = fields.Float(
        string='Total Allowance',
        required=False)
    total_overtime = fields.Float(
        string='Total Overtime',
        required=False)
    total_deduction = fields.Float(
        string='Total Deduction',
        required=False)
    total_net_salary = fields.Float(
        string='Total Net Salary',
        required=False)

    def action_view_payroll_entry_list(self):
        pass

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                emp = self.env['hr.employee'].sudo().search([('id','=',rec.employee_id.id)],limit=1)
                if emp:
                    rec.nik = emp.nik or null
                    rec.job_id = emp.job_id or null
                    rec.job_status = emp.job_status or null
                    rec.emp_status = emp.emp_status or null
                    rec.gender = emp.gender or null
                    rec.npwp = emp.no_npwp or null
                    rec.department_id = emp.department_id or null
                    rec.branch_id = emp.branch_id.id or null
                    rec.area_id = emp.area.id or null
