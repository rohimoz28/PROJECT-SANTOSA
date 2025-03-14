from odoo import models, fields, api
from datetime import date, datetime, timedelta


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    #bank masuk
    transaction_class = fields.Char()
    kode_element_santosa = fields.Char()
    is_jasa_medis = fields.Boolean()
    amount_jasa_medis = fields.Monetary()
    avg_price = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string="Currency")
    item_group_key = fields.Integer()
    name = fields.Char('Name', index='trigram', translate=True)
    penampung_name = fields.Char()
    penampung_description = fields.Char()
    product_detail_ids = fields.One2many('santosa_finance.product_detail', 'product_id')

class ProductCategory(models.Model):
    _inherit = 'product.category'

    #bank masuk
    item_group_key = fields.Integer()
    product_type_id = fields.Many2one('santosa_finance.product_type')
    tipe = fields.Selection([ 
        ('Penjamin', 'Penjamin'),
        ('Item', 'Item'),
        ('RI', 'RI'),
        ('RJ', 'RJ')
    ])