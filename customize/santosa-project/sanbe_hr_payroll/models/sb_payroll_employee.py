from odoo import fields, models, api

class SbPayrollEmployee(models.Model):
    _name = 'sb.payroll.employee'
    _description = 'Payroll Employee'

    name = fields.Char(related='employee_id.name')
    payroll_summary_detail_id = fields.Many2one('sb.payroll.summary.detail', string='Payroll Summary Detail ID')
    payroll_employee_details_ids = fields.One2many('sb.payroll.employee.details', 'payroll_employee_id', string='Payroll Employee Details IDs', required=False)
    payroll_group = fields.Char('Payroll Group')
    period_pay_calc = fields.Date('Period Pay Calc')
    department_id = fields.Many2one('hr.department', string='Department')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    job_id = fields.Many2one('hr.job', string='Job Position')
    job_status = fields.Selection([('permanent', 'Permanent'),
                                   ('contract', 'Contract'),
                                   ('outsource', 'Outsource'),
                                   ('visitor', 'Visitor'),
                                   ('mitra', 'Mitra'),
                                   ('tka', 'TKA'),
                                   ], string='Job Status')
    state = fields.Selection([('draft', 'Draft'),
                              ('req_approval', 'Request For Approval'),
                              ('rejected', 'Rejected'),
                              ('inactive', 'Inactive'),
                              ('approved', 'Approved'),
                              ('hold', 'Hold'),
                              ], string='Status')
    calc_date = fields.Date('Calc Date')
    npwp = fields.Char('Npwp')
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
    gender = fields.Selection([
                              ('male', 'Male'),
                              ('female', 'Female'),
                              ('other', 'Other'),
                              ], string='Gender')
    bank_account = fields.Char('Bank Account')
    atax = fields.Float('ATAX')
    dtax = fields.Float('DTAX')
    total_b_salary = fields.Float('Total B. Salary')
    total_allowance = fields.Float('Total Allowance')
    total_deduction = fields.Float('Total Deduction')
    total_overtime = fields.Float('Total Overtime')
    total_net_salary = fields.Float('Total Net Salary')

class SbPayrollEmployeeDetails(models.Model):
    _name = 'sb.payroll.employee.details'
    _description = 'Payroll Employee Details'

    payroll_employee_id = fields.Many2one('sb.payroll.employee', string='Payroll Employee ID')
    pay_code = fields.Char('Pay Code')
    desc = fields.Char('Description')
    type = fields.Char('Type')
    qty = fields.Float('Qty')
    amount = fields.Char('Amount')
    amount_total = fields.Char('Amount Total')
    amount_total_edited = fields.Char('Amount Total Edited')
