# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class STGInvoiceLines(models.Model):
    _name = 'santosa_finance.stg_invoice_lines' # name_of_module.name_of_class
    _rec_name = 'TransactionNo'
    _description = 'Model Penampung Line' # Some note of table

    # Header
    TransactionNo = fields.Char()
    StatusRecord = fields.Char()
    idTrx = fields.Integer()
    NoTrxKlaim = fields.Char()
    TransactionDate = fields.Datetime()
    SalesPoint = fields.Char()
    ElementDetailKey = fields.Char()
    ElementDetailName = fields.Char()
    ElementTypeKey = fields.Char()
    ElementTypeName = fields.Char()
    ItemGroupKey = fields.Char()
    ItemGroupName = fields.Char()

    #tambahan baru
    TrxClass = fields.Char()
    TrxName = fields.Char()
    DocRefNo = fields.Char()
    DokterCode = fields.Char()
    DokterName = fields.Char()
    CostPrice_JasaMedik = fields.Float()
    IsPPN = fields.Integer()
    acc_id = fields.Integer()
    Qty = fields.Integer()
    Price = fields.Float()
    Total = fields.Float()
    CostPrice_AVG = fields.Float()
    DiscountItem = fields.Float()
    DiscountDokter = fields.Float()
    DiscountSubtotal = fields.Float()
    Amount = fields.Float()
    DPP = fields.Float()
    PPN = fields.Float()
    DPP_PPN = fields.Float()
    NonPPN = fields.Float()
    Omzet = fields.Float()
    Revenue = fields.Float()
    COA_patient_Key = fields.Char()
    COA_patient_Name = fields.Char()
    StatusRecordDD = fields.Char()
    flag_line = fields.Integer()
    flag_line_dua = fields.Integer()
    product_id_odoo = fields.Integer()
    EnteredDate = fields.Datetime()
    PopulatedTime = fields.Datetime()
    IsPPN_Boolean = fields.Boolean()

    