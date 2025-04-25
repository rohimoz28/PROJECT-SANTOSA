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
    
class ProductMutation(models.Model):
    _name = 'product.mutation'
    _description = 'Product Mutation Periodically'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    product_id = fields.Many2one('product.product')
    product_tmpl_id = fields.Many2one('product.template', store=True, readonly=True)
    periode = fields.Char('Periode Mutation')
    
    # Quantities fields with default values
    # Quantities fields with default values
    qty_awal = fields.Float('QTY Awal', default=0.0)
    qty_purchase = fields.Float('QTY Purchase', default=0.0)
    qty_return = fields.Float('QTY Return', default=0.0)
    qty_mutation_in = fields.Float('QTY Mutation(In)', default=0.0)
    qty_adj = fields.Float('QTY Adjustment', default=0.0)
    qty_delivery = fields.Float('QTY Delivery(Sale)', default=0.0)
    qty_mutation_out = fields.Float('QTY Mutation(Out)', default=0.0)
    qty_disposal = fields.Float('QTY Disposal', default=0.0)
    
    # Field for final quantity after mutation
    qty_akhir = fields.Float('QTY Akhir', default=0.0, compute='_compute_qty_akhir', store=True)
    
    # Monetary fields with default 0.0 if no value is provided
    cost = fields.Monetary('Cost', default=0.0)
    price = fields.Monetary('Price', default=0.0)
    avg_price = fields.Monetary('Average Price', default=0.0)
    
    # Company and Currency
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    @api.depends('qty_awal', 'qty_purchase', 'qty_return', 'qty_delivery', 'qty_mutation_out', 'qty_mutation_in', 'qty_disposal', 'qty_adj')
    def _compute_qty_akhir(self):
        for record in self:
            # Compute the final quantity (qty_akhir) based on other quantities, including adjustments (qty_adj)
            record.qty_akhir = (
                record.qty_awal + 
                record.qty_purchase + 
                record.qty_mutation_in + 
                record.qty_adj -  # Include adjustments
                record.qty_delivery - 
                record.qty_mutation_out - 
                record.qty_return - 
                record.qty_disposal
            )