from odoo import models, fields, api,tools,_
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
        ('Sanbe Group', 'Sanbe Group'),
        ('Jkn', 'Jaminan Kesehatan Nasional')
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
                
class AJPResPartner(models.Model):
    _name = 'ajp.res.partner'
    _description = 'AJP Res Partner'
    _order = 'tipe_customer, name'
    _rec_name = 'display_name'
    _auto = False  # because this is a SQL view

    # === Field Definitions (must match the SELECT columns) ===
    id = fields.Integer()
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    penjamin_code = fields.Char(string='Penjamin Code')
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company')
    branch_id = fields.Many2one('res.branch', string='Branch')  # Assuming you have branch module
    tipe_customer = fields.Char(string='Customer Type')
    active = fields.Boolean(string='Active')
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=False)
    supplier_rank = fields.Integer()
    customer_rank = fields.Integer()
    is_customer = fields.Boolean(string="Is Customer", store=True)
    is_supplier = fields.Boolean(string="Is Vendor",  store=True)
    penjamin_code = fields.Integer()
    external_id = fields.Char(string="External ID", )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    id,
                    id AS partner_id,
                    penjamin_code,
                    name,
                    company_id,
                    branch_id,
                    tipe_customer,
                    active,
                    CASE 
                        WHEN tipe_customer IS NOT NULL THEN UPPER(tipe_customer) || ' - ' || name
                        ELSE name
                    END AS display_name,
                    is_customer,
                    external_id,
                    is_supplier,
                    supplier_rank,
                    customer_rank
                FROM res_partner 
                WHERE active = true and coalesce(tipe_customer,'') in ('Asuransi','Umum','Korporasi','Sanbe Group','Jkn')
            )
        """)

    @api.depends('tipe_customer', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.tipe_customer:
                record.display_name = f"{record.tipe_customer.upper()} - {record.name}"
            else:
                record.display_name = record.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = args + ['|', '|',
                         ('tipe_customer', operator, name),
                         ('penjamin_code', operator, name),
                         ('name', operator, name)] if name else args
        return self.search(domain, limit=limit).name_get()