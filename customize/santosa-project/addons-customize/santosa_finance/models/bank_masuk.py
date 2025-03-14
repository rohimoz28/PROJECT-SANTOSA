from odoo import models, fields, api
from datetime import date, datetime, timedelta


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    flag = fields.Selection([ 
        ('Bank Masuk', 'Bank Masuk'),
        ('Alokasi Bank Masuk INS Corp', 'Alokasi Bank Masuk INS Corp'),
        ('Alokasi Bank Masuk Umum', 'Alokasi Bank Masuk Umum')
    ])

    #bank masuk
    no_bank_masuk = fields.Char()
    tgl_bank_masuk = fields.Date()
    amount_bank_masuk = fields.Char()
    nama_bank = fields.Char()
    keterangan = fields.Char()
    status = fields.Char()

    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()
    transaction_date = fields.Char()

    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()

    #alokasi bank masuk ins corp
    no_alokasi = fields.Char()
    tgl_alokasi = fields.Char()
    tgl_transaksi_alokasi = fields.Date()
    jumlah_alokasi = fields.Char()
    no_tag_klaim = fields.Char()
    no_fpk_ref_doc = fields.Char()
    amount_tagihan = fields.Monetary()
    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()

    #alokasi bank masuk umum
    no_invoice = fields.Char()
    doc_rev = fields.Char()
    amount_invoice = fields.Monetary()
    is_revisi = fields.Boolean()
    revision_count = fields.Char()