from odoo import models, fields, api
from datetime import date, datetime, timedelta
from contextlib import ExitStack, contextmanager
from textwrap import shorten
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    groupby,
    index_exists,
    is_html_empty,
    create_index,
)
from odoo import _
from collections import defaultdict
from itertools import groupby
from operator import itemgetter



class AccountMove(models.Model):
    _inherit = 'account.move'

    transaction_no = fields.Char(string="Transaction No")
    odoo_transaction_no = fields.Char()
    no_trx_base = fields.Char()
    transaction_date = fields.Date()
    invoice_no = fields.Char()
    tanggal_invoice = fields.Datetime('Tanggal TRX', default=lambda self: fields.Date.context_today(self))
    registration_date = fields.Datetime()
    registration_no = fields.Char()
    sales_point = fields.Char()
    periode_perawatan_from = fields.Datetime()
    periode_perawatan_to = fields.Datetime()

    med_rec_number = fields.Char()
    patient_name = fields.Char()
    no_sep_ref_no = fields.Char()
    total_invoice = fields.Monetary(string='Total Amount',store = True)
    total_diskon = fields.Monetary()
    unit_code = fields.Char()
    unit_name = fields.Char()
    penjamin_utama_code = fields.Char()
    penjamin_key = fields.Many2one('santosa_finance.penjamin')
    penjamin_utama_name = fields.Char()
    amount_utama = fields.Float()
    status_invoice = fields.Char()
    status_staging = fields.Char()
    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()
    journal_type = fields.Many2one('offset.type')
    cost_price = fields.Monetary(string = "Cost Price",help="Nilai dari CostPrice terakhir (mengacu pada metode LastBuy atau LastHNA", default=0.0)
    cost_price_avg= fields.Monetary(string = "Cost Price AVG", default=0.0)
    cost_price_last_date = fields.Date(string = "Cost Price Last Date", help="Tanggal saat nilai cost price terakhir tersebut berlaku")
    cost_price_last_based = fields.Char(string = "Cost Price Last Based", help="Menjelaskan nilai cost price terakhir ini didapat dari metode apa, misalnya LastBuy atau LastHNA")

    #AR
    tgl_klaim = fields.Date()
    amount_tagihan = fields.Monetary()
    status_ar_klaim = fields.Char()
    no_fpk_ref_doc = fields.Char()
    no_tag_klaim = fields.Char()
    is_revisi = fields.Boolean()
    revision_count = fields.Char()

    # Fields from Invoice Alloc Beban
    penjamin_code = fields.Char(string="Penjamin Code")
    penjamin_name = fields.Char(string="Penjamin Name")
    penjamin_name_id = fields.Many2one('res.partner')
    amount_penjamin = fields.Monetary(string="Amount Penjamin", currency_field='currency_id')


    #tambahan terakhir
    rowkey = fields.Char()
    admission_date = fields.Datetime()
    discharge_date = fields.Datetime()
    line_of_sales = fields.Char()
    sales_group = fields.Selection([
        ('Biling', 'Biling'),
        ('KemoJKN', 'KemoJKN'),
        ('ProlanisJKN', 'ProlanisJKN'),
        ('RefVarBB', 'RefVarBB')
    ])
    corp_group = fields.Selection([
        ('Corp Asuransi', 'Corp Asuransi'),
        ('JKN', 'JKN'),
        ('KemoJKN', 'KemoJKN'),
        ('ProlanisJKN', 'ProlanisJKN'),
        ('UMUM', 'UMUM')
    ])
    doc_type = fields.Char()
    dpp = fields.Monetary()
    ppn = fields.Monetary()
    dpp_ppn = fields.Monetary()
    non_ppn = fields.Monetary()
    omzet = fields.Monetary()
    revenue = fields.Monetary()
    total_debit = fields.Monetary()
    total_credit = fields.Monetary()
    offset_amt = fields.Monetary()
    jurnal_name = fields.Char(related='journal_id.name',store=True)
    status_record = fields.Char()
    accounting_time_periode = fields.Datetime(string="Accounting Periode", default=lambda self: fields.Datetime.now())
    accounting_date_periode = fields.Date('Accounting Periode')
    populated_time = fields.Datetime(string="Populated Time", default=lambda self: fields.Datetime.now())
    is_klaim = fields.Boolean(default=False, string='AR Klaim')
    invoice_amount_claim = fields.Monetary(string="Amount Klaim ",default=0)
    amount_claim_aloc = fields.Monetary(string="Nilai Teralokasi",default=0)
    amount_claim_paids = fields.Monetary(string="Nilai Terbayar",default=0)
    total_amt_claim = fields.Monetary(string='Total Amount Claim',store=True)
    no_bill = fields.Char(string='No. Tagihan')
    populated_date = fields.Date(string="Populated Date", compute='_compute_populated_date', store=True)
    journal_periode = fields.Date('Jurnal Date', default=lambda self: fields.Date.context_today(self))
    journal_ajp = fields.Char('Jurnal No')
    journal_ajp_id = fields.Many2one('journal.ajp','Jurnal No') #Un-Used
    journal_type = fields.Char('Tipe Jurnal',) #Un-Used
    journal_type_id = fields.Many2one('account.journal','Tipe Jurnal', default=lambda self: self._get_journal())
    journal_code = fields.Char('Kode Jurnal', related='journal_id.code')
    branch_id = fields.Many2one('res.branch','Branch')
    move_type = fields.Selection(
        selection_add=[('ar_klaim', 'AR Klaim')],
        ondelete={'ar_klaim': 'set default'}
    )

    def _reset_values(self):
        for line in self:
            pass
        
    # @api.onchange('journal_type_id')
    # def _set_journal_id(self):
    #     for line in self:
    #         line.journal_id = line.journal_type_id.id
        
    @api.depends('is_klaim')    
    def _set_journal_id_klaim(self):
        for line in self:
            line.journal_id = self.env['account.journal'].search([('name','=','AR Klaim')],limit=1).id or False

    # @api.depends('invoice_line_ids.invoice_amount', 'invoice_line_ids.invoice_amount_claim')
    # def _compute_total_klaim(self):
    #     for line in self:
            # line.total_invoice = sum(line.invoice_line_ids.mapped('invoice_amount')) or 0
            # line.total_amt_claim = sum(line.invoice_line_ids.mapped('invoice_amount_claim')) or 0
            # line.total_debit = sum(line.invoice_line_ids.mapped('debit')) or 0
            # line.total_credit = sum(line.invoice_line_ids.mapped('credit')) or 0
            # line.amount_total_signed = sum(line.invoice_line_ids.mapped('invoice_amount_claim')) or 0

    @api.model
    def _get_journal(self):
        jurnal_umum = self.env['account.journal'].search([('code', 'ilike', 'jum')], limit=1)
        return jurnal_umum.id if jurnal_umum else False

    @api.onchange('state')
    def _update_accounting_date(self):
        for line in self:
            if line.state != 'draft':
                line.accounting_date_periode = fields.Date.context_today(self)

    @api.model
    def create(self, vals):
        vals['invoice_date_due'] = fields.Date.context_today(self) + timedelta(days=30)
        return super(AccountMove, self).create(vals)

    @api.depends('populated_time')
    def _compute_populated_date(self):
        for rec in self:
            rec.populated_date = rec.populated_time.date() if rec.populated_time else False
            
    binary_checksum = fields.Char()
    location = fields.Char()
    last_update = fields.Datetime()
    status_sinkronisasi = fields.Selection([
        ('Proses Pembentukan AR Harian', 'Proses Pembentukan AR Harian'),
        ('Proses Penyesuaian AR', 'Proses Penyesuaian AR'),
        ('Selesai', 'Selesai')
    ], default='Proses Pembentukan AR Harian')
    is_not_first_calculate = fields.Boolean()

    temp_invoice_no = fields.Char(compute='_compute_temp_invoice_no')
    los = fields.Integer()
    cobname = fields.Char()
    offset_id = fields.Many2one(
        'account.move',
        )
    list_trans_offset = fields.One2many('santosa_finance.transaction_tracking','offset_id', domain="[('partner_id','=',partner_id)]")
    pelayanan = fields.Selection([('pelayanan','AR Pelayanan'),('non pelayanan','AR Non Pelayanan')],'type AR',default='non pelayanan')

    list_invoice_offsets = fields.Many2many(
        'account.move', 
        'account_move_link_rel',  # Relation table
        'offset_id', 'linked_offset_id',  # Foreign keys in the relation table
        string='Linked Account Moves',
        help='Link multiple account move records', 
        # domain=[('status_invoice','=','open')]
        
    )

    @api.onchange('partner_id')
    def _onchange_field(self):
        self.penjamin_name_id = self.partner_id.id
    
    def action_post(self):
        # Call the original method first (important)
        res = super(AccountMove, self).action_post()
        for move in self:
            move.accounting_date_periode = fields.Date.context_today(move)
            move.accounting_time_periode = fields.Datetime.now()
            if not move.transaction_date:
                move.transaction_date = fields.Date.context_today(move)
            if not move.invoice_date:
                move.invoice_date = fields.Date.context_today(move)
        return res

    @api.depends('status_invoice', 'sales_point', 'penjamin_name')
    def _compute_temp_invoice_no(self):
        for record in self:
            if record.status_invoice == 'Closed':
                record.temp_invoice_no = record.invoice_no
            else:
                record.temp_invoice_no = ''

    # overriding method bawaan odoo di account_move.py
    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending on its type.
        :param show_ref:    A flag indicating if the display name must include the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        name = ''
        if self.state == 'draft':
            name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
                'ar_klaim': _('Draft AR Klaim'),  # ✅ Tambahan move_type 'ar_klaim'
            }.get(self.move_type, _('Draft Move'))  # fallback untuk safety
            name += ' '
        if not self.name or self.name == '/':
            if self.id:
                name += '(* %s)' % str(self.id)
        else:
            name += self.name
            if self.env.context.get('input_full_display_name'):
                if self.partner_id:
                    name += f', {self.partner_id.name}'
                if self.date:
                    name += f', {format_date(self.env, self.date)}'
        return name + (f" ({shorten(self.ref, width=50)})" if show_ref and self.ref else '')

    @api.model_create_multi
    def create(self, vals_list):
        # Override move_type sebelum create
        for vals in vals_list:
            if self.env.context.get('is_ar_klaim'):
                vals['move_type'] = 'ar_klaim'  # override jadi 'ar_klaim'

        # Panggil metode bawaan terlebih dahulu
        moves = super(AccountMove, self).create(vals_list)
        # Fungsionalitas tambahan untuk nomor transaksi
        for move, vals in zip(moves, vals_list):
            if 'odoo_transaction_no' not in vals or not vals['odoo_transaction_no']:
                prefix = 'INV'
                today = datetime.today()
                year = today.strftime('%Y')
                month = today.strftime('%m')
                day = today.strftime('%d')

                # Generate the sequence code for the current year and month
                sequence_code = f'account.move.transaction.no.{year}.{month}'

                # Check if the sequence exists
                sequence = self.env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)
                if not sequence:
                    # Create the sequence if it doesn't exist
                    self.env['ir.sequence'].sudo().create({
                        'name': f'Transaction Number {year}/{month}',
                        'code': sequence_code,
                        'implementation': 'no_gap',
                        'prefix': f'{prefix}/{year}/{month}/',
                        'padding': 5,
                        'number_increment': 1,
                        'number_next_actual': 1,
                    })

                move.odoo_transaction_no = self.env['ir.sequence'].next_by_code(sequence_code) or '/'

        return moves

    def button_create_invoice_lines(self):
        am = self.env['account.move'].search([('status_sinkronisasi', '=', 'Proses Pembentukan AR Harian')])
        print(am, "ini yang mau dieksekusi")
        for record in am:
            nilai = self.env['account.move.line'].search([('move_id', '=', record.id)])
            codenya = None
            for nilai_baru in nilai:
                codenya = nilai_baru.account_id.code

            myacc = self.env['account.account'].sudo().search([('name', '=', 'Account Receivable')])

            # Buat query untuk mengelompokkan dan menghitung total unit_price berdasarkan populate_date
            record.env.cr.execute("""
                SELECT populate_date, SUM(price_subtotal) as total_unit_price
                FROM account_move_line
                WHERE move_id = %s
                GROUP BY populate_date
            """, (record.id,))
            query_result = record.env.cr.fetchall()

            tambahan = []
            seen_dates = set()
            for row in query_result:
                populate_date = row[0]
                total_unit_price = row[1]

                if populate_date not in seen_dates:
                    tambahan.append({
                        'product_id': False,
                        'debit': total_unit_price,
                        'move_id': record.id,
                        'account_id': myacc.id,
                        'populate_date': populate_date,
                        'name': None,
                        'credit': 0.0,
                    })
                    seen_dates.add(populate_date)
            tambahan = [item for item in tambahan if item['populate_date'] is not None]
            print(tambahan, "ini nilai yang disisipkan")
            mbaru = self.env['account.move.line'].create(tambahan)
            record.line_ids += mbaru
            if record.is_not_first_calculate == False:
                record.status_sinkronisasi = 'Proses Penyesuaian AR'
            else:
                record.status_sinkronisasi = 'Selesai'

    def penyesuaian_kembali(self):
        print("jalan awal")
        am = self.env['account.move'].search([('status_sinkronisasi', '=', 'Selesai')])
        print(am, "ini record am untuk penyesuaian kembali")
        for record in am:
            print("fungsi penyesuaian kembali berjalan")

            move_lines = self.env['account.move.line'].search([('need_to_calculate', '=', True)])
            print(move_lines, "ini yang akan harus disesuaikan lagi")
            print(move_lines.move_id, "in move_id yang akan harus disesuaikan lagi")
            if move_lines:
                hapus_ar = self.env['account.move.line'].search([('move_id', '=', move_lines.move_id.id),('product_id', '=', False)])
                print(hapus_ar, "ini ar yang harus dihapus")
                print("ini ada yang harus disesuaikan")
                deleted_rows = hapus_ar.sudo().unlink()
                print(f"Jumlah baris yang dihapus: {deleted_rows}")
                move_lines.need_to_calculate = False
                move_lines.move_id.is_not_first_calculate = True
                move_lines.move_id.status_sinkronisasi = 'Proses Pembentukan AR Harian'
            else:
                print("ga ada yang harus disesuaikan")

    def delete_ar_bawaan(self):
        print("jalan awal")
        am = self.env['account.move'].search([('status_sinkronisasi', '=', 'Proses Penyesuaian AR')])
        for record in am:
            print("fungsi delete AR bawaan jalan")

            move_lines = self.env['account.move.line'].search([('populate_date', '=', False),('debit', '!=', 0),('move_id', '=', record.id)])
            print(move_lines, "ini yang akan dihapus")

            deleted_rows = move_lines.sudo().unlink()

            print(f"Jumlah baris yang dihapus: {deleted_rows}")
            record.status_sinkronisasi = 'Selesai'

    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        # if unbalanced_moves:
        #     error_msg = _("An error has occurred.")
        #     for move_id, sum_debit, sum_credit in unbalanced_moves:
        #         move = self.browse(move_id)
        #         error_msg += _(
        #             "\n\n"
        #             "The move (%s) is not balanced.\n"
        #             "The total of debits equals %s and the total of credits equals %s.\n"
        #             "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
        #             move.display_name,
        #             format_amount(self.env, sum_debit, move.company_id.currency_id),
        #             format_amount(self.env, sum_credit, move.company_id.currency_id),
        #             move.journal_id.name)
        #     raise UserError(error_msg)