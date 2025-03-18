# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class MatrixPostingDetails(models.Model):
    _name = 'santosa_finance.matrix_posting_key_details' # name_of_module.name_of_class
    _rec_name = 'posting_key'
    _description = 'Maxtrix Posting Key Details' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    posting_key = fields.Char()
    posting_key_type = fields.Selection([ 
        ('Standard', 'Standard'),
        ('Reversal', 'Reversal')
    ])
    account_type = fields.Selection([ 
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    ])
    seq_item = fields.Char()
    trx_class = fields.Char()
    matrix_posting_id = fields.Many2one('santosa_finance.matrix_posting_key')
    flag_subledger = fields.Selection([ 
        ('T', 'T'),
        ('F', 'F')
    ])
    reversal_posting_key = fields.Char()
    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()
    description = fields.Char(tracking=True)

class MatrixPostingSub(models.Model):
    _name = 'santosa_finance.matrix_posting_sub' # name_of_module.name_of_class
    _rec_name = 'posting_key'
    _description = 'Maxtrix Posting Key Sub' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    posting_key = fields.Char()
    posting_key_type = fields.Selection([ 
        ('Standard', 'Standard'),
        ('Reversal', 'Reversal')
    ])
    account_type = fields.Selection([ 
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    ])
    subledger_type = fields.Selection([ 
        ('Cust', 'Cust'),
        ('Vendor', 'Vendor'),
        ('Unit', 'Unit'),
        ('Dokter', 'Dokter')
    ])