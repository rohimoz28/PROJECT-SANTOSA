from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
import pytz
from babel.dates import format_datetime


class STGPayDetail(models.Model):
    _name = 'santosa_finance.stg_pay_detail' # name_of_module.name_of_class
    _rec_name = 'TransactionNo'
    _description = 'Model Penampung Pay Detail' # Some note of table
    
    # Header
