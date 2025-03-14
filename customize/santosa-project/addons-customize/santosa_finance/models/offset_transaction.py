# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class OffsetTransaction(models.Model):
    _name = 'santosa_finance.offset_transaction' # name_of_module.name_of_class
    _rec_name = 'odoo_transaction_no'
    _description = 'Offset Transaction' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()
    transaction_date = fields.Date()
    offset_no = fields.Char()
    offset_date = fields.Date()
    offset_type = fields.Selection([ 
        ('Biaya Admin Bank', 'Biaya Admin Bank'),
        ('Biaya Pajak', 'Biaya Pajak'),
        ('Biaya Audit', 'Biaya Audit'),
        ('Write Off', 'Write Off')
    ])
    offset_description = fields.Char()
    document_ref_number = fields.Char()
    attachment_document_ref = fields.Binary() 
    total_amount_offset = fields.Float()
    remarks = fields.Char()
    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()

    def test(self):
        pass

class OffsetTransactionDetails(models.Model):
    _name = 'santosa_finance.offset_transaction_details' # name_of_module.name_of_class
    _rec_name = 'offset_number'
    _description = 'Offset Transaction' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    offset_number = fields.Char()
    #doc = fields.Char() masih nunggu dokumen fsd untuk detailnya harus gimana
    doc_date = fields.Date()
    doc_amount = fields.Float()
    remarks = fields.Char()