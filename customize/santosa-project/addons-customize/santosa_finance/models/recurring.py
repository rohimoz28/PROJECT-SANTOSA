# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class RecurringSetup(models.Model):
    _name = 'santosa_finance.recurring_setup' # name_of_module.name_of_class
    _rec_name = 'recurring_id'
    _description = 'Recurring Setup' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    recurring_id = fields.Char()
    recurring_transaction_date = fields.Date()
    interval = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Interval', default='monthly')
    time_of_recurring = fields.Datetime()
    start_date_from = fields.Date()
    description = fields.Char()
    flag_in_active = fields.Boolean()
    status = fields.Char()

class RecurringSetupDetails(models.Model):
    _name = 'santosa_finance.recurring_setup_details' # name_of_module.name_of_class
    _rec_name = 'recurring_id'
    _description = 'Recurring Setup Details' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    recurring_id = fields.Many2one('santosa_finance.recurring_setup')
    coa_id = fields.Many2one('account.account')
    coa_description = fields.Char()
    debit_or_credit = fields.Selection([
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    ], string='Interval')

class RecurringSetupDetailDetails(models.Model):
    _name = 'santosa_finance.recurring_setup_detail_details' # name_of_module.name_of_class
    _rec_name = 'recurring_id'
    _description = 'Recurring Setup Details' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    recurring_id = fields.Many2one('santosa_finance.recurring_setup')
    subsidiary_type = fields.Selection([
        ('Customer', 'Customer'),
        ('Vendor', 'Vendor'),
        ('DLL', 'DLL'),
    ], string='Subsidiary Type')
    subsidiary_name = fields.Char()
    amount = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string="Currency")
