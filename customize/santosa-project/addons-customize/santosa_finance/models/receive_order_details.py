from odoo import models, fields, api
from datetime import date, datetime, timedelta


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()


    no_ro = fields.Char()
    kode = fields.Char()
    sat = fields.Char()

    jumlah = fields.Integer()
    tipe = fields.Selection([ 
        ('Obat', 'Obat'),
        ('Alkes', 'Alkes'),
        ('Consumeable', 'Consumeable')
    ])