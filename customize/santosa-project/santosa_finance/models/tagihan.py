# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class TagihanHeaders(models.Model):
    _name = 'santosa_finance.tagihan_headers' # name_of_module.name_of_class
    _rec_name = 'odoo_transaction_no'
    _description = 'Tagihan Headers' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()

    transaction_date = fields.Date()
    penjamin_code = fields.Char()
    penjamin_name = fields.Char()
    tgl_klaim = fields.Date()
    no_tag_klaim = fields.Char()
    no_fpk_ref_doc = fields.Char()
    amount_tagihan = fields.Monetary()
    status_ar_klaim = fields.Char()
    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()
    currency_id = fields.Many2one('res.currency', string="Currency")

class TagihanLine(models.Model):
    _name = 'santosa_finance.tagihan_line' # name_of_module.name_of_class
    _rec_name = 'invoice_no'
    _description = 'Tagihan Line' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    tagihan_id = fields.Many2one('santosa_finance.tagihan_headers', string="No Tag Klaim")
    invoice_no = fields.Char()
    invoice_date = fields.Date()
    sep_ref_no = fields.Char()
    med_rec_number = fields.Char()
    patient_name = fields.Char()
    invoice_amount_claim = fields.Monetary()
    status_invoice = fields.Char()
    currency_id = fields.Many2one('res.currency', string="Currency")