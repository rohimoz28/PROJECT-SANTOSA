# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class ProductDetail(models.Model):
    _name = 'santosa_finance.product_detail' # name_of_module.name_of_class
    _description = 'Model Product Detail' # Some note of table

    product_id = fields.Many2one('product.template')
    transaction_date = fields.Date()
    item_code = fields.Char()
    no_trx = fields.Char()
    name = fields.Char()
    # price = fields.Float()
    unit_price = fields.Float()
    quantity = fields.Integer()
    total_price = fields.Float()