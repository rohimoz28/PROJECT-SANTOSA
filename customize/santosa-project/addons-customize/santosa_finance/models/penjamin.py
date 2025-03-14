# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class Penjamin(models.Model):
    _name = 'santosa_finance.penjamin' # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Model Master Penjamin' # Some note of table

    # Header
    name = fields.Char()
    id_penjamin = fields.Integer()