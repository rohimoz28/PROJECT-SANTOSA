from odoo import models, fields, api
from datetime import date, datetime, timedelta

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    # Header
    
    effective_date_from = fields.Date()
    currency_rate = fields.Float()
    description = fields.Char()

class AccountAccount(models.Model):
    _inherit = 'account.account'

    description = fields.Char()
    typical_balance = fields.Monetary()
    posting_type = fields.Char()
    account_group_code = fields.Char()
    parent_account = fields.Many2one('account.account')
    flag_sub_account = fields.Char()
    flag_subsidiary = fields.Char()
    flag_inactive = fields.Boolean()
    group_name = fields.Char()
    level = fields.Char()