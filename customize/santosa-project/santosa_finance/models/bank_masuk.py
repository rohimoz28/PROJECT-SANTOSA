from odoo import models, fields, api
from datetime import date, datetime, timedelta
date_format = "%Y-%m-%d"



class AccountBankStatement(models.Model):
    _name = 'cash.bank'
    _description = 'kas Bank Masukan Purpose'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'state,id'

    name = fields.Char(default='New')
    bank_type = fields.Selection([('Bank','Bank'), ('Kas','Kas')], string="Bank Type", default="Bank", tracking=True)
    journal_id = fields.Many2one('account.journal', string="Bank Account", tracking=True, required=True, store=True)
    account_id = fields.Many2one('account.account', related='journal_id.default_account_id', string="Bank Account", tracking=True)
    currency_id = fields.Many2one('res.currency', string='Mata Uang', compute="_compute_currency_id", store=True)
    no_trx = fields.Char(default='New', required=True, tracking=True)

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for record in self:
            if record.journal_id:
                record.currency_id = record.journal_id.default_account_id.currency_id
            else:
                record.currency_id = self.env.user.company_id.currency_id

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self._compute_currency_id()
            
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    balance_start = fields.Monetary(string="Saldo Awal", store=True, default=0, tracking=True)
    balance_end = fields.Monetary(string="Saldo Akhir", store=True, compute="_calculate_ending_balance", tracking=True)
    debit = fields.Monetary(string="Masuk", store=True, compute="_calculate_ending_balance", tracking=True)
    # credit = fields.Monetary(string="Keluar", store=True, default=0)
    total_ump = fields.Monetary(string="Total UMP", store=True, default=0, tracking=True)
    total_uar = fields.Monetary(string="Total UAR", store=True, default=0, tracking=True)
    total_alokasi = fields.Monetary(string="Total Alokasi", store=True, default=0, tracking=True)
    branch_id = fields.Many2one('res.branch', string="Branch", index=True, default=lambda self: self.env.user.branch_id.id)
    account_periode_name = fields.Char(related = 'account_periode_id.name', string="Accounting Periode",store=True)
    
    def _get_running_periode(self):
        return self.env['acc.periode.closing'].search([('state_process', '=', 'running'),('branch_id', '=', self.env.user.branch_id.id)], order='id DESC', limit=1)

    account_periode_id = fields.Many2one('acc.periode.closing', string="Accounting Periode", domain="[('state_process', '=', 'running'),('branch_id', '=',branch_id)]", default=_get_running_periode )
    state = fields.Selection([('draft','Draft'),('open','Open'),('posted','Posted'),('cancel','Cancel')], string="Status", default="draft", tracking=True)
    line_ids = fields.One2many('account.bank.statement','cash_bank_id',string="Keluar", store=True)

    @api.depends('balance_start','debit', 'line_ids.balance')
    def _calculate_ending_balance(self):
        for line in self:
            total_debit = sum(order_line.balance for order_line in line.line_ids)
            line.debit = total_debit
            if line.balance_start :
                line.balance_end = line.balance_start + line.debit

    def unlink(self):
        return super().unlink()    
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('bank_type') == 'Kas':
    #             vals['name'] = self.env['ir.sequence'].next_by_code('cash.bank.kas') or '/'
    #         else:
    #             vals['name'] = self.env['ir.sequence'].next_by_code('cash.bank.bank') or '/'
    #     return super().create(vals_list)


    def act_close(self):
        for line in self:
            line.state = 'posted'
            
    def act_open(self):
        for line in self:
            line.state = 'open'
            if line.bank_type == 'Kas':
                line.name = self.env['ir.sequence'].next_by_code('cash.bank.kas') or '/'
            else:
                line.name = self.env['ir.sequence'].next_by_code('cash.bank.bank') or '/'


            
    def act_cancel(self):
        for line in self:
            line.state = 'cancel'

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    flag = fields.Selection([ 
        ('Bank Masuk', 'Bank Masuk'),
        ('Alokasi Bank Masuk INS Corp', 'Alokasi Bank Masuk INS Corp'),
        ('Alokasi Bank Masuk Umum', 'Alokasi Bank Masuk Umum')
    ])

    #bank masuk
    cash_bank_id = fields.Many2one('cash.bank',string="Cas Bank",cascade=True)
    no_bank_masuk = fields.Char()
    tgl_bank_masuk = fields.Date()
    amount_bank_masuk = fields.Char()
    nama_bank = fields.Char()
    balance = fields.Monetary(string="Amount", store=True, default=0)
    partner_name = fields.Char(string="Cust/Penjamin", related="partner_id.display_name", store=True)
    is_uar = fields.Boolean('UAR ?', default=False)
    partner_id = fields.Many2one('res.partner',string="Cust/Penjamin")
    notes =  fields.Char()
    keterangan = fields.Char()
    status = fields.Char()
    account_move_id = fields.Many2one('account.move')
    transaction_no = fields.Char(related='account_move_id.transaction_no', store=True)
    odoo_transaction_no = fields.Char()
    transaction_date = fields.Datetime()

    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()

    #alokasi bank masuk ins corp
    no_alokasi = fields.Char()
    tgl_alokasi = fields.Char()
    tgl_transaksi_alokasi = fields.Date()
    jumlah_alokasi = fields.Char()
    no_tag_klaim = fields.Char()
    no_fpk_ref_doc = fields.Char()
    amount_tagihan = fields.Monetary()
    status_transaksi = fields.Char()
    populated_time = fields.Datetime(string="Populated Time", default=lambda self: fields.Datetime.now())

    @api.depends('populated_time')
    def _compute_populated_date(self):
        for rec in self:
            rec.populated_date = rec.populated_time.date() if rec.populated_time else False
            
    
    populated_date = fields.Date(string="Populated Date", compute='_compute_populated_date', store=True)
    account_periode_number = fields.Char(related = 'account_periode_id.name', string="Accounting Periode",store=True)
    account_periode_id = fields.Many2one('acc.periode.closing', )
    
    @api.depends('cash_bank_id','account_move_id')
    def _set_acc_periode_cahsbank(self):
        for line in self:
            if line.cash_bank_id:
                line.account_periode_id = line.cash_bank_id.account_periode_id.id
                if line.account_move_id:
                    line.partner_id = line.account_move_id.penjamin_name_id.id
                    line.amount_tagihan = line.account_move_id.amount_total_signed
    
    periode_closing_date = fields.Date(related = 'account_periode_id.open_periode_to', store=True)
    #alokasi bank masuk umum
    no_invoice = fields.Char(related='account_move_id.invoice_no', store=True)
    doc_rev = fields.Char()
    amount_invoice = fields.Monetary(related='account_move_id.amount_total_signed', store=True)
    is_revisi = fields.Boolean()
    revision_count = fields.Char()
    date = fields.Date(
        compute='_compute_date_index', inverse='_comp_pass', store=True,
        index=True,
    )
    
    def _comp_pass(self):
        for line in self:
            pass