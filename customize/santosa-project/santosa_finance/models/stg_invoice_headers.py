# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
import pytz
from babel.dates import format_datetime


class STGInvoiceHeaders(models.Model):
    _name = 'santosa_finance.stg_invoice_headers' # name_of_module.name_of_class
    _rec_name = 'TransactionNo'
    _description = 'Model Penampung Headers' # Some note of table

    # Header
    TransactionNo = fields.Char()
    StatusRecord = fields.Char()
    RegistrationNo = fields.Char()
    RegistrationDate = fields.Datetime()
    InvoiceNo = fields.Char()
    InvoiceDate = fields.Datetime()
    Invoice_ClosedDate = fields.Datetime()
    StatusInvoice = fields.Char()
    Medrec = fields.Char()
    PatientName = fields.Char()
    SEPNo = fields.Char()
    AdmissionDate = fields.Datetime()

    DischargeDate = fields.Datetime()
    LOS = fields.Char()
    SalesGroup = fields.Char()
    CorpGroup = fields.Char()
    DocType = fields.Char()
    SalesPoint = fields.Char()
    LocationName = fields.Char()
    TotalInvoice = fields.Float()
    TotalAmount = fields.Float()
    TotalDiscount = fields.Float()
    DPP = fields.Float()
    PPN = fields.Float()
    DPP_PPN = fields.Float()
    NonPPN = fields.Integer()
    Omzet = fields.Float()
    Revenue = fields.Float()
    PenjaminKey = fields.Integer()
    PenjaminCode = fields.Char()
    PenjaminName = fields.Char()
    COBName = fields.Char()
    EnteredDate = fields.Datetime()
    PopulatedTime = fields.Datetime()
    CostPrice_AVG = fields.Float()
    CostPrice_LAST = fields.Float(string = "Cost Price",help="Nilai dari CostPrice terakhir (mengacu pada metode LastBuy atau LastHNA", default=0.0)
    CostPrice_LAST_Date = fields.Date(string = "Cost Price Last Date", help="Tanggal saat nilai cost price terakhir tersebut berlaku")
    CostPrice_LAST_Based = fields.Char(string = "Cost Price Last Based", help="Menjelaskan nilai cost price terakhir ini didapat dari metode apa, misalnya LastBuy atau LastHNA")
