from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class STGClaimLines(models.Model):
    _name = 'santosa_finance.stg_claim_lines' # name_of_module.name_of_class
    _description = 'Model Penampung Klaim Line' # Some note of table


    TableInfo = fields.Char()
    RowKey = fields.Char()
    PeriodeAwal = fields.Date()
    PeriodeAkhir = fields.Date()
    TAGKlaimNo = fields.Char()
    StatusRecord = fields.Char()
    TAGKlaimDate = fields.Date()
    TAGKlaimSent = fields.Date()
    TAGKlaimDueDate = fields.Date()
    RefNo_FPKNo = fields.Char()
    TAGKlaimLastStatus = fields.Char()
    SEPNo = fields.Char()
    TransactionNO = fields.Char()
    IsCetak = fields.Boolean()
    PrintDate = fields.Datetime()
    InvoiceNo = fields.Char()
    PenjaminKey = fields.Integer()
    PenjaminCode = fields.Char()
    PenjaminName = fields.Char()
    COBName = fields.Char()
    PayorCode = fields.Char()
    PayorName = fields.Char()
    Medrec = fields.Char()
    PatientName = fields.Char()
    AmountKlaim =  fields.Float(default=0.0)
    Description = fields.Char()
    EnteredDate = fields.Datetime()
    ModifiedDate = fields.Datetime()
    PopulatedTime = fields.Datetime()
    Binary_Checksum = fields.Integer()