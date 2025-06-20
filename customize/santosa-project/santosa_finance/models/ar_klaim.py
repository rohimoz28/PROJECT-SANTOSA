from odoo import fields, models, api
from odoo.exceptions import ValidationError


class arKlaim(models.Model):
    _name = 'ar.klaim'
    _description = 'AR Klaim'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    claim_date = fields.Date(string="Tanggal Klaim")
    claim_number = fields.Char(string="No. Klaim", required=True)
    bill_number = fields.Char(string="No. Tagihan")
    guarantor = fields.Many2one(comodel_name="res.partner", 
                                string="Penjamin", 
                                ondelete="cascade")
    claim_value = fields.Monetary(string="Nilai Klaim", 
                                  currency_field="currency_id",
                                  required=True, 
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
        default="in_process"
    )
    ar_klaim_ids = fields.One2many(
        comodel_name="ar.klaim.detail",
        inverse_name="ar_klaim_id",
        string="Detail Klaim"
    )


    @api.constrains('claim_value')
    def _check_claim_value(self):
        for record in self:
            if record.claim_value < 0:
                raise ValidationError("Nilai klaim tidak boleh negatif.")


class arKlaimDetail(models.Model):
    _name = 'ar.klaim.detail'
    _description = 'AR Klaim Detail'

    ar_klaim_id = fields.Many2one(
        comodel_name="ar.klaim",
        string="Klaim",
        ondelete="cascade"
    )
    trx_number = fields.Char(string="No TRX")
    invoice_id = fields.Many2one(
        comodel_name="account.move", 
        string="Invoice Name",
    )
    Invoice_number = fields.Char(related="invoice_id.invoice_no", string="No Invoice")
    billing_date = fields.Date(string="Tanggal Invoice") 
    sep_number = fields.Char(string="No SEP")
    mr_number = fields.Char(string="No MR")
    invoice_amount = fields.Monetary(string="Amount Invoice",
                                     currency_field='currency_id',
                                     store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='ar_klaim_id.currency_id',
        store=True,
    )


    @api.constrains('invoice_amount')
    def _check_invoice_amount(self):
        for record in self:
            if  record.invoice_amount < 0:
                raise ValidationError("Amount Invoice tidak boleh negatif.")


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



