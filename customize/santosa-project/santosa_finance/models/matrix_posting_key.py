# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class MatrixPostingKey(models.Model):
    _name = 'santosa_finance.matrix_posting_key' # name_of_module.name_of_class
    _rec_name = 'doc_name'
    _description = 'Maxtrix Posting Key' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    posting_key = fields.Char()
    posting_key_name = fields.Char()
    description = fields.Char()
    doc_name = fields.Many2one('res.partner')
    doc_ref_number = fields.Char()
    idc = fields.Char()
    valid_from = fields.Date()
    tipe = fields.Selection([ 
        ('Active', 'Active'),
        ('In Active', 'In Active')
    ])
    name = fields.Char(tracking=True)