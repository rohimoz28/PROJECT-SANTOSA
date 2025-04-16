from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


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

TMS_ENTRY_STATE = [
    ('draft', 'Draft'),
    ('running', 'Running'),
    ('approved', "Approved"),
    ('done', "Close"),
    ('transfer_payroll', 'Transfer Payroll'),
]


class SbPayrollSummary(models.Model):
    _name = 'sb.payroll.summary'
    _description = 'Payroll Summary'


    # hr_tmsentry_summary_id = fields.Many2one(comodel_name='hr.tmsentry.summary', string='TMS Entry', ondelete='cascade')
    periode_id = fields.Many2one('hr.opening.closing', string='Periode', index=True)
    employee_group_id = fields.Selection(selection=EMP_GROUP1, string='Employee P Group')
    branch_id = fields.Many2one(comodel_name='res.branch', string='Business Unit', index=True)
    department_id = fields.Many2one('hr.department', string='Sub Department')

    # Relation to child
    payroll_detail_ids = fields.One2many(comodel_name='sb.payroll.summary.detail', inverse_name='payroll_id', 
                                         string='Payroll ID', index=True)
    
    def action_view_payroll_summary(self):
        pass


class SbPayrollSummaryDetail(models.Model):
    _name = 'sb.payroll.summary.detail'
    _description = 'Payroll Summary Detail'


    # Relation to parent
    payroll_id = fields.Many2one(comodel_name='sb.payroll.summary', string='Payroll Summary ID', 
                                 ondelete='cascade', index=True)

    nik = fields.Char(string='NIK')
    employee_id = fields.Many2one('hr.employee', string='Employee Name', index=True)
    job_id = fields.Many2one('hr.job', string='Job Position')
    total_basic_salary = fields.Float(string='T. Basic Salary')
    total_overtime = fields.Float(string='T. Overtime')
    total_allowance = fields.Float(string='T. Allowance')
    total_deduction = fields.Float(string='T. Deduction')
    net_salary = fields.Float(string='Take Home Pay',required=False)
    state = fields.Selection(selection=TMS_ENTRY_STATE, string='Status', readonly=True, default='draft')


    def payrol_summary_detail_button(self):
        # pass
        # Menyaring payroll employee berdasarkan payroll_summary_detail_id yang ada
        payroll_employee = self.env['sb.payroll.employee'].search([
            ('payroll_summary_detail_id', '=', self.id)
        ], limit=1)  # Mengambil satu record pertama yang ditemukan
        
        if not payroll_employee:
            raise UserError("No related Payroll Employee Detail found.")

        # Mengarahkan pengguna ke form `SbPayrollEmployee`
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Payroll Employee',
            'res_model': 'sb.payroll.employee',
            'view_mode': 'form',
            'view_id': self.env.ref('sanbe_hr_payroll.sb_payroll_employee_form').id,  # Ganti dengan ID form view yang sesuai
            'res_id': payroll_employee.id,  # Mengarah ke record sb.payroll.employee yang sesuai
            'target': 'current',  # Mengarahkan di jendela yang sama
        }
        return action