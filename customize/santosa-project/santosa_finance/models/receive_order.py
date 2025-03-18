from odoo import models, fields, api
from datetime import date, datetime, timedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()

    transaction_date = fields.Char()

    no_ro = fields.Char()
    surat_jalan = fields.Char()
    tgl_ro = fields.Date()

    group_ro = fields.Char()
    no_po = fields.Char()
    tanggal_po = fields.Date()
    nama_pabrik = fields.Char()
    nama_vendor = fields.Char()
    warehouse = fields.Char()
    sub_total = fields.Monetary()
    disc = fields.Integer()
    extra_disc = fields.Integer()
    ppn_percent = fields.Integer()

    ppn = fields.Integer()
    total = fields.Monetary()
    status = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()

    is_revisi = fields.Boolean()
    revision_count = fields.Char()