# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class SalesPointCOAConfig(models.Model):
    _name = 'santosa_finance.sales_point_coa_config' # name_of_module.name_of_class
    _rec_name = 'sales_point'
    _description = 'Model Config Sales Point COA' # Some note of table

    # Header
    sales_point = fields.Char()
    item_group = fields.Char()
    income_account = fields.Many2one('account.account')
    expense_account = fields.Many2one('account.account')