from odoo import fields, models, api


class SbPayrollSummaryDetail(models.Model):
    _name = 'sb.payroll.summary.detail'
    _description = 'Detail of Payroll Summary'

    employee_id = fields.Char(
        string='Employee ID',
        required=False)
    employee_name = fields.Char(
        string='Employee Name',
        required=False)
    nik = fields.Char(
        string='NIK',
        required=False)
    basic_salary = fields.Float(
        string='Basic Salary',
        required=False)
    overtime = fields.Float(
        string='Overtime',
        required=False)
    allowance = fields.Float(
        string='T. Allowance',
        required=False)
    deduction = fields.Float(
        string='T. Deduction',
        required=False)
    net_salary = fields.Float(
        string='T. Net Salary',
        required=False)
    master_id = fields.Many2one(comodel_name='sb.payroll.entry.list', string='Payroll Entry List')


