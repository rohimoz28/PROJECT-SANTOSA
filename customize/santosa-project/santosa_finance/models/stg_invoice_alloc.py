# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class STGInvoiceAlloc(models.Model):
    _name = 'santosa_finance.stg_invoice_alloc' # name_of_module.name_of_class
    _rec_name = 'TransactionNo'
    _description = 'Model Penampung Alloc' # Some note of table

    # Header
    TransactionNo = fields.Char()
    PiutangNumber = fields.Char()
    PiutangID = fields.Integer()
    DocType = fields.Char()
    AllocType = fields.Char()
    TransactionDate = fields.Datetime()
    Amount = fields.Float()
    PenjaminKey = fields.Integer()
    account_odoo = fields.Integer()
    PenjaminCode = fields.Integer()
    PenjaminName = fields.Char()
    PatientName = fields.Char()
    EnteredDate = fields.Datetime()
    PopulatedTime = fields.Datetime()
    Binary_Checksum = fields.Integer()