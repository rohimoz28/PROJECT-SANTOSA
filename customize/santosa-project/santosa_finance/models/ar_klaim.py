from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class arKlaim(models.Model):
    _name = 'ar.klaim'
    _description = 'AR Klaim'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", index=True, store=True, compute="_compute_trx_name")
    claim_date = fields.Date(string="Tanggal Klaim")
    claim_number = fields.Char(string="No. Klaim", index=True, required=True)
    bill_number = fields.Char(string="No. Tagihan")
    guarantor = fields.Many2one(comodel_name="res.partner", 
                                string="Penjamin", 
                                ondelete="cascade")
    claim_value = fields.Monetary(string="Nilai Klaim", 
                                  currency_field="currency_id",
                                  default=0, 
                                  compute='total_claim',
                                  store=True)
    amt_claim_value = fields.Monetary(string="Total Tagihan Klaim",
                                  currency_field="currency_id",
                                  default=0, 
                                  compute='total_claim',
                                  store=True)
    payer = fields.Many2one(comodel_name="res.partner", 
                                string="Payor", 
                                ondelete="cascade")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    state = fields.Selection(
        selection=[
            # ('draft','Draft'),
            ('in_process', 'In Process'),
            ('partial_settled','Partial Settled'),
            ('close','Close'),
            ('cancel','Cancel'),
        ],
        string="Status", 
        track_visibility='onchange',
        default="in_process"
    )
    ar_klaim_ids = fields.One2many(
        comodel_name="ar.klaim.detail",
        inverse_name="ar_klaim_id",
        string="Detail Klaim"
    )
    
    PopulatedTime = fields.Datetime()
    PopulatedDime = fields.Date(string="Populated Date", compute='_compute_populated_date', store=True)
    
    total_invoice = fields.Datetime()


    @api.depends('claim_number', 'ar_klaim_ids.invoice_id.name')
    def _compute_name(self):
        for rec in self:
            trx_names = rec.ar_klaim_ids.mapped('invoice_id.name')
            trx_part = ', '.join(filter(None, trx_names)) if trx_names else ''
            if rec.claim_number and trx_part:
                rec.name = f"{rec.claim_number} | {trx_part}"
            elif rec.claim_number:
                rec.name = rec.claim_number
            else:
                rec.name = trx_part
            
    @api.depends('PopulatedTime')
    def _compute_populated_date(self):
        for rec in self:
            rec.PopulatedDime = rec.PopulatedTime.date() if rec.PopulatedTime else False


    @api.depends('ar_klaim_ids.invoice_amount','ar_klaim_ids.amt_klaim')
    def total_claim(self):
        for order in self:
            order.amt_claim_value = sum(order.ar_klaim_ids.mapped('invoice_amount')) or 0
            order.claim_value = sum(order.ar_klaim_ids.mapped('amt_klaim')) or 0
            
    @api.depends('TotalAmountClaim')
    def _inverse_field(self):
        pass

    @api.constrains('claim_value')
    def _check_claim_value(self):
        for record in self:
            if record.claim_value < 0:
                raise ValidationError("Nilai klaim tidak boleh negatif.")

    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'

class arKlaimDetail(models.Model):
    _name = 'ar.klaim.detail'
    _description = 'AR Klaim Detail'

    ar_klaim_id = fields.Many2one(
        comodel_name="ar.klaim",
        string="Klaim",
        ondelete="cascade"
    )
    trx_number = fields.Char(string="No TRX",related="invoice_id.name")
    invoice_id = fields.Many2one(
        comodel_name="account.move", 
        string="No.TRX",
    )
    Invoice_number = fields.Char(related="invoice_id.invoice_no", string="Invoice No")
    billing_date = fields.Date(string="Invoice Date") 
    sep_number = fields.Char(string="No SEP")
    mr_number = fields.Char(string="No MR")
    invoice_amount = fields.Monetary(string="Invoice Amount",
                                     currency_field='currency_id',
                                     compute='_set_invoice_detail',
                                     inverse='_reset_value_amt',                                     
                                     store=True)
    guarantor = fields.Many2one(comodel_name="res.partner", 
                                string="Penjamin", 
                                ondelete="cascade")
    payer = fields.Many2one(comodel_name="res.partner", 
                                string="Payor", 
                                ondelete="cascade", related='ar_klaim_id.payer')
    amt_klaim = fields.Monetary(string="Amount klaim",
                                     currency_field='currency_id',
                                     store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='ar_klaim_id.currency_id',
        store=True,
    )
    diff_amt = fields.Monetary(string="Selisih", currency_field='currency_id', compute="_compute_selisih",store=True)
    PopulatedTime = fields.Datetime()
    PopulatedDime = fields.Date(string="Populated Date", compute='_compute_populated_date', store=True)
    status_invoice = fields.Char()

    @api.depends('PopulatedTime')
    def _compute_populated_date(self):
        for rec in self:
            rec.PopulatedDime = rec.PopulatedTime.date() if rec.PopulatedTime else False


    def _reset_value_amt(self):
        for line in self:
            pass

    @api.constrains('amt_klaim','invoice_amount')
    def _check_invoice_amount(self):
        for record in self:
            if  record.amt_klaim < 0:
                raise UserError("Amount Invoice tidak boleh negatif.")
            # if  record.amt_klaim > record.invoice_amount:
            #     raise UserError("Transaksi Lebih Bayar!!")

    @api.depends('invoice_id')
    def _set_invoice_detail(self):
        for record in self:
            if record.invoice_id:
                record.guarantor = record.invoice_id.penjamin_name_id.id or False
                record.billing_date = record.invoice_id.invoice_date
                record.status_invoice = record.invoice_id.status_invoice
                record.mr_number = record.invoice_id.med_rec_number
                record.sep_number = record.invoice_id.no_sep_ref_no
                
    # button eye
    def ar_klaim_invoice_detail_button(self):
        self.ensure_one()
        
        if not self.invoice_id:
            raise ValidationError("Invoice belum dipilih")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            # 'view_id': self.env.ref('account.view_move_form').id if self.env.ref('account.view_move_form') else False,
            'target': 'current'
        }


    @api.depends('invoice_amount', 'amt_klaim')
    def _compute_selisih(self):
        for rec in self:
            rec.diff_amt = (rec.invoice_amount or 0.0) - (rec.amt_klaim or 0.0)