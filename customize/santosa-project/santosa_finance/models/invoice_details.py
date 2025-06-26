from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import pytz
from babel.dates import format_datetime


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    transaction_date = fields.Datetime()
    no_trx = fields.Char(related='invoice_id.transaction_no',store=True)
    document_trx_date = fields.Date(related='invoice_id.transaction_date',store=True)
    transaction_class = fields.Char()
    group = fields.Char()
    item = fields.Char()
    no_invoice_farmasi = fields.Char()
    nomor_invoice = fields.Char(related='invoice_id.invoice_no', store=True)
    dokter_code = fields.Char()
    dokter_name = fields.Char()
    unit_code = fields.Char()
    unit_name = fields.Char()
    idTrx = fields.Integer()

    med_rec_number = fields.Char(string="Med. Record", related='invoice_id.med_rec_number', store=True)
    no_sep_ref_no = fields.Char(string="No. SEP", related='invoice_id.no_sep_ref_no', store=True)
    registration_no = fields.Char()

    patient_name = fields.Char()
    penjamin_name_id = fields.Many2one('res.partner', related='invoice_id.penjamin_name_id')
    concat_field = fields.Char(string='Transaksi')
    invoice_amount_claim = fields.Monetary(string="Amount Klaim ",default=0)
    amount_total_signed = fields.Monetary(string="Amount Invoice ", related='invoice_id.amount_total_signed', store=True)
    invoice_amount = fields.Monetary(string="Amount Invoice ", related='invoice_id.amount_total_signed', store=True)
    amount_bank_masuk = fields.Monetary()
    jumlah_alokasi = fields.Monetary()
    sisa_amount_claim = fields.Monetary()
    no_bank_masuk = fields.Char()
    tgl_bank_masuk = fields.Date()
    no_alokasi = fields.Char()
    tgl_alokasi = fields.Date()
    tgl_transaksi_alokasi = fields.Date()
    status_invoice = fields.Char(related='invoice_id.status_invoice',string="Status",store=True)
    is_revisi = fields.Boolean()
    cost_price = fields.Monetary(string = "Cost Price",help="Nilai dari CostPrice terakhir (mengacu pada metode LastBuy atau LastHNA", default=0.0)
    cost_price_avg= fields.Monetary(string = "Cost Price AVG", default=0.0)
    cost_price_last_date = fields.Date(string = "Cost Price Last Date", help="Tanggal saat nilai cost price terakhir tersebut berlaku")
    cost_price_last_based = fields.Char(string = "Cost Price Last Based", help="Menjelaskan nilai cost price terakhir ini didapat dari metode apa, misalnya LastBuy atau LastHNA")

    #tambahan terakhir
    rowkey = fields.Char()
    element_detail_key = fields.Char()
    element_detail_name = fields.Char()
    element_type_key = fields.Char()
    element_type_name = fields.Char()
    item_group_key = fields.Char()
    item_group_name = fields.Char()
    sales_point = fields.Selection([ 
        ('[1] Rawat Jalan', '[1] Rawat Jalan'),
        ('[2] Rawat Inap', '[2] Rawat Inap'),
        ('[3] Farmasi Bebas', '[3] Farmasi Bebas'),
        ('[4] UGD', '[4] UGD')
    ])
    is_ppn = fields.Char()
    dpp = fields.Monetary()
    ppn = fields.Monetary()
    dpp_ppn = fields.Monetary()
    non_ppn = fields.Monetary()
    omzet = fields.Monetary()
    revenue = fields.Monetary()
    costprice_jasamedik = fields.Float()
    discount_subtotal = fields.Float()
    discount_dokter = fields.Float()
    discount_item = fields.Float()
    coa_patient_key = fields.Char()
    coa_patient_name = fields.Char()
    status_record = fields.Char()
    populated_time = fields.Datetime()
    populate_date = fields.Datetime(string="Populated Date", compute='_compute_populated_date', store=True)

    @api.depends('populated_time')
    def _compute_populated_date(self):
        for rec in self:
            rec.populate_date = rec.populated_time.date() if rec.populated_time else False
            
    entered_date = fields.Datetime()
    last_update = fields.Datetime()
    binary_checksum = fields.Char()
    accounting_time_periode = fields.Datetime(related='move_id.accounting_time_periode')
    accounting_date_periode = fields.Date(related='move_id.accounting_date_periode')
    need_to_calculate = fields.Boolean()
    flag = fields.Integer()
    pelayanan = fields.Selection([('pelayanan','AR Pelayanan'),('non pelayanan','AR Non Pelayanan')], 'type AR',store=True, default='non pelayanan', related='move_id.pelayanan')
    formatted_datetime = fields.Char(string='Formatted Datetime', compute='_compute_formatted_datetime')
    CostPrice_AVG = fields.Float()
    
    #claim purpose
    paid_state_klaim = fields.Boolean(default=False, string='Status Bayar')
    is_klaim = fields.Boolean(related="move_id.is_klaim",string='AR Klaim')
    invoice_id = fields.Many2one('account.move',string="No TRX", domain="[('is_klaim', '=',False),('state', '!=','draft')]",)
    invoice_date = fields.Date(related='invoice_id.invoice_date',store=True)
    amount_klaim = fields.Float(string="Amount Klaim ",default=0)
    amount_diff = fields.Float(string="Selisih")
    invoice_state = fields.Selection(related='invoice_id.state',string="Status",store=True)
    
    @api.depends('invoice_id','invoice_amount_claim','invoice_amount')
    def _get_selisih(self):
        for line in self:
            if line.invoice_id:
                line.name = line.invoice_id.name
                line.currency_id = line.invoice_id.currency_id.id
                line.account_id = self.env['account.account'].search([('account_type','=','liability_payable')],limit=1).id
                line.compute_all_tax = False
                line.partner_id =line.invoice_id.penjamin_name_id.id
                # line.amount_diff = line.invoice_amount - line.invoice_amount_claim
                # line.sisa_amount_claim = line.invoice_amount - line.invoice_amount_claim
                # line.price_unit = line.invoice_amount_claim
                # line.price_subtotal = line.invoice_amount_claim
                # line.patient_name = line.invoice_id.patient_name
                
        
    @api.onchange('invoice_id','invoice_amount_claim','invoice_amount')
    def _set_default_claim_val(self):
        for line in self:
            line._get_selisih()

    @api.depends('product_id', 'product_uom_id')
    def _compute_price_unit(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            if line.move_id.is_sale_document(include_receipts=True):
                document_type = 'sale'
            elif line.move_id.is_purchase_document(include_receipts=True):
                document_type = 'purchase'
            else:
                document_type = 'other'

    @api.model_create_multi
    def create(self, vals_list):
        moves = self.env['account.move'].browse({vals['move_id'] for vals in vals_list})
        container = {'records': self}
        move_container = {'records': moves}
        with moves._check_balanced(move_container),\
             moves._sync_dynamic_lines(move_container),\
             self._sync_invoice(container):
            lines = super().create([self._sanitize_vals(vals) for vals in vals_list])
            container['records'] = lines

        for line in lines:
            if line.move_id.state == 'posted':
                line._check_tax_lock_date()

        if not self.env.context.get('tracking_disable'):
            # Log changes to move lines on each move
            tracked_fields = [fname for fname, f in self._fields.items() if hasattr(f, 'tracking') and f.tracking and not (hasattr(f, 'related') and f.related)]
            ref_fields = self.env['account.move.line'].fields_get(tracked_fields)
            empty_values = dict.fromkeys(tracked_fields)
            for move_id, modified_lines in lines.grouped('move_id').items():
                if not move_id.posted_before:
                    continue
                for line in modified_lines:
                    if tracking_value_ids := line._mail_track(ref_fields, empty_values)[1]:
                        line.move_id._message_log(
                            body=_("Journal Item %s created", line._get_html_link(title=f"#{line.id}")),
                            tracking_value_ids=tracking_value_ids
                        )

        lines.move_id._synchronize_business_models(['line_ids'])
        lines._check_constrains_account_id_journal_id()
        return lines

    account_receivable_total = fields.Monetary(string='Account Receivable Total', compute='_compute_account_receivable_total')

    @api.depends('move_id.line_ids.debit', 'move_id.line_ids.credit')
    def _compute_account_receivable_total(self):
        for line in self:
            if line.account_id.account_type == 'receivable':
                total = sum(l.debit - l.credit for l in line.move_id.line_ids if l.account_id.user_type_id.type == 'receivable')
                line.account_receivable_total = total
            else:
                line.account_receivable_total = 0.0

    def _prepare_create_values(self, vals_list):
        print(vals_list, "iniii _prepare_create_values")
        result_vals_list = super()._prepare_create_values(vals_list)

        return result_vals_list

    @api.ondelete(at_uninstall=False)
    def _prevent_automatic_line_deletion(self):
        if not self.env.context.get('dynamic_unlink'):
            for line in self:
                if line.display_type == 'tax' and line.move_id.line_ids.tax_ids:
                    raise ValidationError(_(
                        "You cannot delete a tax line as it would impact the tax report"
                    ))
                # elif line.display_type == 'payment_term':
                #     raise ValidationError(_(
                #         "You cannot delete a payable/receivable line as it would not be consistent "
                #         "with the payment terms"
                #     ))


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

    def update_account_id(self):
        am = self.env['account.move.line'].search([])
        for record in am:
            print(record.product_id.categ_id.property_account_income_categ_id.id, "ini akun bener nya")
            print(record.account_id.id, "ini akun salah nya")
            record.account_id = record.product_id.categ_id.property_account_income_categ_id.id

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            pass
            # account_type = line.account_id.account_type
            # if line.move_id.is_sale_document(include_receipts=True):
            #     if account_type == 'liability_payable':
            #         raise UserError(_("Account %s is of payable type, but is used in a sale operation.", line.account_id.code))
                # if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
                #     raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
            # if line.move_id.is_purchase_document(include_receipts=True):
            #     if account_type == 'asset_receivable':
            #         raise UserError(_("Account %s is of receivable type, but is used in a purchase operation.", line.account_id.code))
                # if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                #     raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))
