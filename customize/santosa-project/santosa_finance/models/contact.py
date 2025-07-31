from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Header
    
    is_dokter_mitra = fields.Boolean(string="Dokter Mitra", default=False)
    transaction_tracking_ids = fields.One2many(
        comodel_name='santosa_finance.transaction_tracking',
        inverse_name='partner_id')
    di_tracking_ids = fields.One2many(
        comodel_name='santosa_finance.transaction_tracking',
        inverse_name='partner_id', domain=[('flag','=',20)], help="Differed Income"
        )
    hd_tracking_ids = fields.One2many(
        comodel_name='santosa_finance.transaction_tracking',
        inverse_name='partner_id', domain=[('flag','=',10)], help="Hutang Docter"
        )
    ar_jkn_tracking_ids = fields.One2many(
        comodel_name='santosa_finance.transaction_tracking',
        inverse_name='partner_id', domain=[('flag','=',30)], help="AR JKN"
        )
    ar_tracking_ids = fields.One2many(
        comodel_name='santosa_finance.transaction_tracking',
        inverse_name='partner_id', domain=[('flag','=',40)], help="AR"
        )
    ump_tracking_ids = fields.One2many(
        comodel_name='santosa_finance.transaction_tracking',
        inverse_name='partner_id', domain=[('flag','=',50)], help="UMP"
        )
    tipe_customer = fields.Selection([ 
        ('Asuransi', 'Asuransi'),
        ('Umum', 'Umum'),
        ('Korporasi', 'Korporasi'),
        ('Sanbe Group', 'Sanbe Group')
    ])
    is_customer = fields.Boolean(string="Is Customer", compute="_compute_is_customer", inverse="_set_is_customer", store=True)
    is_supplier = fields.Boolean(string="Is Vendor", compute="_compute_is_supplier", inverse="_set_is_supplier", store=True)
    penjamin_code = fields.Integer()
    external_id = fields.Char(string="External ID", )

    @api.depends('customer_rank')
    def _compute_is_customer(self):
        for partner in self:
            partner.is_customer = partner.customer_rank > 0

    @api.depends('supplier_rank')
    def _compute_is_supplier(self):
        for partner in self:
            partner.is_supplier = partner.supplier_rank > 0

    def _set_is_customer(self):
        for partner in self:
            if partner.is_customer:
                partner.customer_rank = 1 if partner.customer_rank == 0 else partner.customer_rank
            else:
                partner.customer_rank = 0

    def _set_is_supplier(self):
        for partner in self:
            if partner.is_supplier:
                partner.supplier_rank = 1 if partner.supplier_rank == 0 else partner.supplier_rank
            else:
                partner.supplier_rank = 0