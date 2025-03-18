# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError

ACCOUNT_DOMAIN = "['&', ('deprecated', '=', False), ('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card','off_balance'))]"


class AkunKategori(models.Model):
    _name = 'santosa_finance.akun_kategori' # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Model Akun Kategori' # Some note of table

    # Header
    name = fields.Char('Name', index='trigram', required=True)
    account_code = fields.Char()
    account_name = fields.Char()
    product_category_id_temp = fields.Integer()
    SalesPoint = fields.Integer()
    penjamin_id = fields.Integer()
    tipe = fields.Selection([ 
        ('Penjamin', 'Penjamin'),
        ('Item', 'Item'),
        ('Jasa', 'Jasa'),
        ('Biaya', 'Biaya')
    ])
    kategori = fields.Selection([ 
        ('Jurnal Pengakuan AR Sementara', 'Jurnal Pengakuan AR Sementara'),
        ('Jurnal Biaya Obat', 'Jurnal Biaya Obat'),
        ('Jurnal Biaya Jasa Medis', 'Jurnal Biaya Jasa Medis'),
        ('Jurnal Pengakuan AR - Diskon', 'Jurnal Pengakuan AR - Diskon'),
        ('Jurnal Pengakuan AR - Pendapatan Lain-lain', 'Jurnal Pengakuan AR - Pendapatan Lain-lain'),
        ('Jurnal Pengakuan AR', 'Jurnal Pengakuan AR')
    ])
    journal_id = fields.Many2one('account.journal')

    akun_kategori_account_income_categ_id = fields.Many2one('account.account', string="Income Account")
    akun_kategori_account_expense_categ_id = fields.Many2one('account.account', string="Expense Account")

    #child_account = fields.Many2one('santosa_finance.akun_kategori')
    child_coa = fields.Many2one('account.account')


    @api.model
    def create(self, values):
        # Duplicate check: searching for existing records with same criteria
        existing = self.search([
            ('account_code', '=', values.get('account_code')),
            ('account_name', '=', values.get('account_name')),
            ('SalesPoint', '=', values.get('SalesPoint')),
            ('penjamin_id', '=', values.get('penjamin_id')),
            ('akun_kategori_account_income_categ_id', '=', values.get('akun_kategori_account_income_categ_id')),
            ('akun_kategori_account_expense_categ_id', '=', values.get('akun_kategori_account_expense_categ_id')),
            ('kategori', '=', values.get('kategori')),
            ('tipe', '=', values.get('tipe')),
        ])

        if existing:
            raise ValidationError("Cannot input duplicate values!")

        # No duplicate found, proceed with creation
        return super(AkunKategori, self).create(values)

    @api.model
    def init(self):
        # Eksekusi SQL untuk membuat index
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_account_category 
            ON santosa_finance_akun_kategori (name, "SalesPoint", tipe);
        """)