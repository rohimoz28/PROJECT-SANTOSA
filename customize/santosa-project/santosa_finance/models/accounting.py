from odoo import models, fields

class AccountingSetup(models.Model):
    _name = 'santosa_finance.accounting_setup'
    _description = 'Accounting Setup'

    accounting_period_from = fields.Date(string='Accounting Period From')
    accounting_period_to = fields.Date(string='Accounting Period To')
    period_no = fields.Integer(string='Period No')
    fiscal_period_from = fields.Date(string='Fiscal Period From')
    fiscal_period_to = fields.Date(string='Fiscal Period To')
    fiscal_period_no = fields.Integer(string='Fiscal Period No')

    # Relasi ke Accounting Setup Details
    setup_detail_ids = fields.One2many('santosa_finance.accounting_setup_details', 'setup_id', string='Setup Details')

class AccountingSetupDetails(models.Model):
    _name = 'santosa_finance.accounting_setup_details'
    _description = 'Accounting Setup Details'

    current_acc_period_no = fields.Integer(string='Current Acc Period No')
    current_acc_month = fields.Char(string='Current Acc Month')
    current_acc_year = fields.Integer(string='Current Acc Year')
    current_fiscal_period_no = fields.Integer(string='Current Fiscal Period No')
    current_fiscal_month = fields.Char(string='Current Fiscal Month')
    current_fiscal_year = fields.Integer(string='Current Fiscal Year')
    status = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('draft', 'Draft')
    ], string='Status')

    # Relasi ke Accounting Setup
    setup_id = fields.Many2one('santosa_finance.accounting_setup', string='Accounting Setup')