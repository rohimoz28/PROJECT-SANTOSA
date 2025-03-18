# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class AlokasiBeban(models.Model):
    _name = 'santosa_finance.alokasi_beban' # name_of_module.name_of_class
    _rec_name = 'registration_no'
    _description = 'Model ALokasi Beban' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    registration_no = fields.Char()
    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()
    invoice_no = fields.Char()
    med_rec_number = fields.Char()
    no_sep = fields.Char()
    penjamin_code = fields.Char()
    penjamin_name = fields.Char()
    piutang_name = fields.Char()
    amount_penjamin = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string="Currency")
    revision_count = fields.Char()

    #tambahan baru
    rowkey = fields.Char()
    piutang_number = fields.Char()
    piutang_id = fields.Char()
    doctype = fields.Char()
    penjamin_key = fields.Char()
    binary_checksum = fields.Char()
    transaction_date = fields.Datetime()
    last_update = fields.Datetime()
    populated_time = fields.Datetime()