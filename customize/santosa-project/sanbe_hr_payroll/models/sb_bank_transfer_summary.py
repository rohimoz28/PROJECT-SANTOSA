from email.policy import default

from odoo import fields, models, api


BANK_TRANSFER_SUMMARY_STATE = [
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

BANK_TRANSFER_SUMMARY_DETAIL_STATE = [
    ('draft', 'Draft'),
    ('approved', "Approved")
]

class SBBankTransferSummary(models.Model):
    _name = 'sb.bank.transfer.summary'
    _description = 'Bank Transfer Summary'

    @api.model
    def _selection1(self):
        return EMP_GROUP1

    employee_group1 = fields.Selection(selection=_selection1, string='Employee P Group')
    nik = fields.Char(string="NIK")
    employee_id = fields.Many2one('hr.employee', index=True)
    bank_name = fields.Char(string='Bank Name')
    bank_account = fields.Char(string='Bank Account')
    amount = fields.Float(string='Bank Transfer Amount', required=False)
    is_approved = fields.Boolean(string='Approved', required=False)
    state = fields.Selection(
        string='State',
        selection=BANK_TRANSFER_SUMMARY_DETAIL_STATE,
        required=False, default="draft")

    _sql_constraints = [
        ('unique_employee_group_state',
         'unique(employee_group1, state)',
         'Duplicate records with the same Employee Group and Status are not allowed.')
    ]