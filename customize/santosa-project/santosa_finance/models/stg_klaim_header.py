from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
import pytz
from babel.dates import format_datetime


class STGCalimeHeaders(models.Model):
    _name = 'santosa_finance.stg_claim_headers' # name_of_module.name_of_class
    _description = 'Model Penampung Claim Headers' # Some note of table
    
    TableInfo = fields.Char()
    RowKey = fields.Char()
    PeriodeAwal = fields.Datetime()
    PeriodeAkhir = fields.Datetime()
    TAGKlaimNo = fields.Char()
    StatusRecord = fields.Char()
    TAGCountDetail = fields.Integer()
    TransactionNO = fields.Char()
    TAGKlaimDate = fields.Date()
    TAGKlaimSent = fields.Date()
    TAGKlaimDueDate = fields.Datetime()
    PayorCode = fields.Char()
    PayorName = fields.Char()
    TotalAmountKlaim = fields.Float(default=0.0)
    EnteredDate = fields.Datetime()
    ModifiedDate = fields.Datetime()
    PopulatedTime = fields.Datetime()
    Binary_Checksum= fields.Integer()