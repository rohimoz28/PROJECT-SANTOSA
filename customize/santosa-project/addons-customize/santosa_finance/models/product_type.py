# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class ProductType(models.Model):
    _name = 'santosa_finance.product_type' # name_of_module.name_of_class
    _rec_name = 'element_type_key'
    _description = 'Product Type' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    element_type_key = fields.Integer()
    element_type_name = fields.Char()
    element_type_description = fields.Char()
    item_group_key = fields.Many2one('product.category')
    versi = fields.Integer()
    inserted_date_from_santosa = fields.Datetime()
    product_template_id = fields.Many2one('product.template')