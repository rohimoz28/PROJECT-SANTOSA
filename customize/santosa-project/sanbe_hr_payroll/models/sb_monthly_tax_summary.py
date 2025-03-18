from email.policy import default

from odoo import fields, models, api

MONTHLY_TAX_SUMMARY_STATE = [
    ('draft', 'Draft'),
    ('approved', "Approved")
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

class SbMonthlyTaxSummary(models.Model):
    _name = 'sb.monthly.tax.summary'
    _description = 'Monthly Tax Summary'

    @api.model
    def _selection1(self):
        return EMP_GROUP1

    employee_group1 = fields.Selection(selection=_selection1, string='Employee P Group')
    employee_id = fields.Many2one('hr.employee', index=True)
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
        default=False,
        required=False)
    state = fields.Selection(
        string='Status',
        selection=MONTHLY_TAX_SUMMARY_STATE,
        default='draft',
        required=False, )
