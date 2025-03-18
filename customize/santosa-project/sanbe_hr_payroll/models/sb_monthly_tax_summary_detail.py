from odoo import fields, models, api

MONTHLY_TAX_SUMMARY_DETAIL_STATE = [
    ('draft', 'Draft'),
    ('approved', "Approved")
]

class SbMonthlyTaxSummaryDetail(models.Model):
    _name = 'sb.monthly.tax.summary.detail'
    _description = 'Monthly Tax Summary Detail'

    employee_id = fields.Char(
        string='Employee ID',
        required=False)
    employee_name = fields.Char(
        string='Employee Name',
        required=False)
    nik = fields.Char(
        string='NIK',
        required=False)
    total_net_salary = fields.Float(
        string='Total Net Salary',
        required=False)
    ptkp = fields.Char(
        string='PTKP',
        required=False)
    ptkp_type = fields.Char(
        string='PTKP Type',
        required=False)
    percentage = fields.Float(
        string='Percentage', 
        required=False)
    amount_tax_ter = fields.Float(
        string='Amount TAX TER',
        required=False)
    is_approved = fields.Boolean(
        string='Approved',
        required=False)
    state = fields.Selection(
        string='Status',
        selection=MONTHLY_TAX_SUMMARY_DETAIL_STATE,
        required=False, )
    # master_id = fields.Many2one(comodel_name='sb.monthly.tax.summary', string='Monthly Tax Summary')
