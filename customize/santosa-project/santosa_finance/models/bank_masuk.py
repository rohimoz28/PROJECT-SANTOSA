from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
date_format = "%Y-%m-%d"


class CashBank(models.Model):
    _name = 'cash.bank'
    _description = 'Kas Bank Masukan Purpose'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'state,id'

    name = fields.Char(related='no_trx'
                       ,tracking=True, store=True, index=True)
    no_trx = fields.Char(required=True, tracking=True, index=True)

    bank_type = fields.Selection([
        ('Bank', 'Bank'),
        ('Kas', 'Kas')
    ], string="Bank Type", default="Bank", tracking=True)

    journal_id = fields.Many2one('account.journal', string="Bank Account", tracking=True, required=True)
    account_id = fields.Many2one('account.account', related='journal_id.default_account_id', string="Bank Account", tracking=True, store=True)

    currency_id = fields.Many2one('res.currency', string='Mata Uang', compute="_compute_currency_id", store=True)

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    branch_id = fields.Many2one('res.branch', string="Branch", index=True, default=lambda self: self.env.user.branch_id)

    balance_start = fields.Monetary(string="Saldo Awal", compute="_get_ending_balance", store=True, tracking=True, currency_field='currency_id')
    balance_end = fields.Monetary(string="Saldo Akhir", compute="_calculate_ending_balance", store=True, default=0, tracking=True, currency_field='currency_id')
    debit = fields.Monetary(string="Masuk", compute="_calculate_ending_balance", store=True, tracking=True, currency_field='currency_id')
    begening_uar = fields.Monetary(string="Saldo Awal UAR", compute="_get_ending_balance", store=True, tracking=True, currency_field='currency_id')
    begining_ump = fields.Monetary(string="Saldo Awal UMP", compute="_get_ending_balance", store=True, tracking=True, currency_field='currency_id')
    end_uar = fields.Monetary(string="Saldo Akhir UAR", compute="_get_ending_balance", store=True, tracking=True, currency_field='currency_id')
    end_ump = fields.Monetary(string="Saldo Akhir UMP", compute="_get_ending_balance", store=True, tracking=True, currency_field='currency_id')

    total_ump = fields.Monetary(string="Total UMP", compute='_compute_ump_uar', tracking=True, store=True, currency_field='currency_id', readonly=True)
    total_uar = fields.Monetary(string="Total UAR", compute='_compute_ump_uar', tracking=True, store=True, currency_field='currency_id', readonly=True)
    total_alokasi = fields.Monetary(string="Total Alokasi", default=0, tracking=True, currency_field='currency_id')

    # display_name = fields.Char(compute='_compute_display_name', store=True)

    account_periode_id = fields.Many2one(
        'acc.periode.closing',
        string="Accounting Periode",
        domain="[('state_process', '=', 'running'),('branch_id', '=',branch_id)]",
        default=lambda self: self._get_running_periode()
    )
    account_periode_name = fields.Char(related='account_periode_id.name', string="Accounting Periode", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel')
    ], string="Status", default="draft", tracking=True)

    line_ids = fields.One2many('account.bank.statement', 'cash_bank_id', string="Keluar")
    aml_line_ids = fields.One2many('account.move.line', 'cash_bank_id', string="Keluar")

    revision_count = fields.Integer(string="Revision", default=0)
    move_id = fields.Many2one('account.move', string="Move Cash Bank", readonly=True)
    
    # COMPUTE METHODS
    @api.depends('journal_id')
    def _compute_currency_id(self):
        for record in self:
            if record.journal_id and record.journal_id.default_account_id:
                record.currency_id = record.journal_id.default_account_id.currency_id
            else:
                record.currency_id = self.env.user.company_id.currency_id

    # Menghitung total UMP dan UAR per document
    @api.depends('line_ids.is_uar', 'line_ids.balance')
    def _compute_ump_uar(self):
        for record in self:
            if record.line_ids:
                uar_lines = record.line_ids.filtered(lambda l: l.is_uar)
                ump_lines = record.line_ids.filtered(lambda l: not l.is_uar)
                record.total_uar = sum(uar_lines.mapped('balance')) or 0.0
                record.total_ump = sum(ump_lines.mapped('balance')) or 0.0
            else:
                record.total_uar = 0.0
                record.total_ump = 0.0

    # Menghitung saldo awal, UM dan UAR
    @api.depends('account_periode_id', 'journal_id')
    def _get_ending_balance(self):
        for record in self:
            if record.journal_id and record.account_periode_id:
                beginning_amt = self.env['account.move.line'].search([
                    ('accounting_periode_id', '=', record.account_periode_id.id),
                    ('flag', '=', 200),
                    ('account_id', '=', record.journal_id.default_account_id.id),
                    ('parent_state','=','posted'),
                    ('balance', '>', 0)
                ],order='id desc', limit=1)
                beginning_bank = self.env['account.move.line'].search([
                    ('accounting_periode_id', '=', record.account_periode_id.id),
                    ('flag', '=', 110),
                    ('account_id', '=', record.journal_id.default_account_id.id),
                    ('parent_state','=','posted'),
                    ('balance', '>', 0)
                ])
                query = """ select id,end_uar,end_ump from cash_bank
                            where account_periode_id = %s
                            and journal_id = %s and branch_id = %s
                            and state = 'posted'
                            order by id desc limit 1
                """
                self.env.cr.execute(query, (record.account_periode_id.id, record.journal_id.id, record.branch_id.id))
                last_cashbank = self.env.cr.dictfetchone()
                if last_cashbank:
                    record.begening_uar = last_cashbank.get('end_uar', 0.0)
                    record.begining_ump = last_cashbank.get('end_ump', 0.0)
                else:
                    record.begening_uar = 0.0
                    record.begining_ump = 0.0
                beginning_amt_balance = beginning_amt.balance if beginning_amt else 0.0
                beginning_bank_total = sum(beginning_bank.mapped('balance')) or 0.0
                # record.begening_uar = total_uar or 0.0
                # record.begining_ump = total_ump or 0.0
                record.balance_start = beginning_amt_balance + beginning_bank_total

    @api.depends('balance_start', 'line_ids.balance')
    def _calculate_ending_balance(self):
        for rec in self:
            total_debit = sum(line.balance for line in rec.line_ids)
            rec.debit = total_debit
            rec.balance_end = rec.balance_start + rec.debit
            rec.end_uar = rec.begening_uar + rec.total_uar
            rec.end_ump = rec.begining_ump + rec.total_ump

    # UTILITY METHOD
    def _get_running_periode(self):
        periode = self.env['acc.periode.closing'].search([
            ('state_process', '=', 'running'),
            ('branch_id', '=', self.env.user.branch_id.id),
            ('open_periode_from', '<=', fields.Datetime.now()),
            ('open_periode_to', '>=', fields.Datetime.now())
        ], order='open_periode_to desc', limit=1)
        return periode

    # ACTIONS
    def act_open(self):
        for rec in self:
            rec.state = 'open'
            # rec.name = self.env['ir.sequence'].next_by_code(
            #     'cash.bank.kas' if rec.bank_type == 'Kas' else 'cash.bank.bank'
            # ) or '/'

    def act_close(self):
        self.ensure_one()
        for rec in self:
            rec.state = 'posted'
            if rec.move_id:
                existing_lines = self.env['account.move.line'].search([('cash_bank_id', '=', rec.id)])
                # if not existing_lines:
                self.env['account.move.line'].create({
                    'name': ' ' + rec.name,
                    'move_id': rec.move_id.id,
                    'account_id': rec.account_id.id,
                    'debit': rec.debit,
                    'credit': 0.0,
                    'flag': 110,
                    'balance': rec.debit,
                    'cash_bank_id': rec.id,
                    'date': fields.Date.today(),
                })
                uar_lines = rec.line_ids.filtered(lambda l: l.is_uar)
                ump_lines = rec.line_ids.filtered(lambda l: not l.is_uar)
                total_uar = sum(uar_lines.mapped('balance')) or 0.0
                total_ump = sum(ump_lines.mapped('balance')) or 0.0
                if total_uar > 0:
                    self.env['account.move.line'].create({
                        'name': rec.name,
                        'move_id': rec.move_id.id,
                        'account_id': rec.journal_id.suspense_account_id.id,
                        'credit': rec.debit,
                        'debit': 0.0,
                        'flag': 110,
                        'balance': -total_uar,
                        'cash_bank_id': rec.id,
                        'date': fields.Date.today(),
                    })
                if total_ump > 0:
                    self.env['account.move.line'].create({
                        'name': rec.name,
                        'move_id': rec.move_id.id,
                        'account_id': rec.journal_id.profit_account_id.id,
                        'credit': rec.debit,
                        'debit': 0.0,
                        'flag': 110,
                        'balance': -total_ump,
                        'cash_bank_id': rec.id,
                        'date': fields.Date.today(),
                    })
                for line in rec.line_ids:
                    get_last_trans = self.env['santosa_finance.transaction_tracking'].search([('partner_id','=',line.partner_id.id)], order='id desc', limit=1)
                    tracking_vals = {
                        'entered_date': line.transaction_date.date() if line.transaction_date else fields.Date.today(),
                        'document_no': rec.name,
                        'transaction_date': line.transaction_date.date() if line.transaction_date else fields.Date.today(),
                        'transaction_no': line.name or line.no_bank_masuk or 'No Transaction',
                        'odoo_transaction_no': rec.move_id.name if rec.move_id else False,
                        'description': line.name,
                        'flag': 50,
                        'amount_debit': 0.0,
                        'amount_credit': -line.balance,
                        'beginning_balance': get_last_trans.ending_balance or 0.0,
                        'ending_balance': get_last_trans.ending_balance - line.balance,
                        'journal_number': rec.journal_id.code if rec.journal_id else False,
                        'partner_id': line.partner_id.id if line.partner_id else False,
                        'account_move_id': rec.move_id.id if rec.move_id else False,
                        'currency_id': rec.currency_id.id if rec.currency_id else False,
                    }
                    print(tracking_vals)
                    self.env['santosa_finance.transaction_tracking'].sudo().create(tracking_vals)
                rec.move_id.action_post()
                
    def act_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_revision(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        periode = self.account_periode_id

        if not (periode and periode.open_periode_from <= today <= periode.open_periode_to):
            # raise UserError(_("Revisi hanya bisa dilakukan di dalam periode yang aktif."))
            reversing_lines_vals = []
            for line in self.move_id.line_ids:
                reversing_line = {
                    'account_id': line.account_id.id,
                    'name': 'Reversal of: ' + (line.name or ''),
                    'move_id': self.move_id.id,
                    'debit': line.credit,
                    'credit': line.debit,
                    'balance': -(line.balance),  # Assuming you use 'balance' field
                    'date': fields.Date.today(),
                    'partner_id': line.partner_id.id,
                    'currency_id': line.currency_id.id,
                    'amount_currency': -line.amount_currency if line.amount_currency else 0.0,
                    'analytic_account_id': line.analytic_account_id.id,
                    'cash_bank_id': line.cash_bank_id.id,
                }
                reversing_lines_vals.append(reversing_line)

        if self.move_id:
            self.move_id.button_cancel()
            self.move_id.line_ids.unlink()
            self.move_id.state = 'draft'
            for tracking in self.env['santosa_finance.transaction_tracking'].search([('odoo_transaction_no','=',self.move_id.name)]):
                if tracking:
                    tracking.unlink()
                    
        self.state = 'open'        
        self.revision_count += 1
        self.message_post(body=f"Kas Bank Revisi ke : {self.revision_count}")

    def action_create_move(self):
        self.ensure_one()

        journal = self.env.ref('santosa_finance.id_cash_bank')
        default_debit_account = self.journal_id.default_account_id
        credit_account = (
            self.journal_id.loss_account_id
            or self.journal_id.profit_account_id
            or self.journal_id.suspense_account_id
        )

        if not default_debit_account or not credit_account:
            raise UserError("Missing account configuration on journal.")

        move_vals = {
            'ref': self.name,
            'journal_id': journal.id,
            'date': fields.Date.context_today(self),
            'transaction_date': fields.Date.context_today(self),
            'invoice_date_due': fields.Date.context_today(self),
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'move_type': 'cash_bank',
            'auto_post': 'no',
            'accounting_periode_id': self.account_periode_id.id,
            'branch_id': self.branch_id.id,
            'line_ids': [],
            'user_id': self.env.user.id,
        }
        move = self.env['account.move'].sudo().create(move_vals)
        self.move_id = move.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            open_proc = self.env['cash.bank'].search([('account_periode_id','=',vals.get('account_periode_id')),('state','=','draft')])
            if open_proc:
                raise UserError("Tidak bisa membuat Cash Bank baru, karena masih ada Cash Bank di periode yang sama dengan status Draft.")
            duplicate_cash_bank = self.env['cash.bank'].search([('no_trx','ilike',vals.get('no_trx'))])
            if duplicate_cash_bank:
                raise UserError("Cannot Create duplicate Cash Bank with the same No. Transaction.")
            journal = self.env.ref('santosa_finance.id_cash_bank')
            journal_id = vals.get('journal_id')
            journal_obj = self.env['account.journal'].browse(journal_id)

            debit_account = journal_obj.default_account_id
            credit_account = (
                journal_obj.loss_account_id.id
                or journal_obj.profit_account_id.id
                or journal_obj.suspense_account_id.id
            )

            if not debit_account or not credit_account:
                raise UserError("Missing account configuration on journal.")

            move_vals = {
                'name':  vals.get('no_trx'),
                # 'ref':  vals.get('no_trx') or vals.get('name'),
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'transaction_date': fields.Date.context_today(self),
                'invoice_date_due': fields.Date.context_today(self),
                'company_id': vals.get('company_id') or self.env.company.id,
                'currency_id': vals.get('currency_id') or self.env.user.company_id.currency_id.id,
                'move_type': 'cash_bank',
                'auto_post': 'no',
                'accounting_periode_id': vals.get('account_periode_id'),
                'branch_id': vals.get('branch_id') or self.env.user.branch_id.id,
                'line_ids': [],
                'user_id': self.env.user.id,
            }
            move = self.env['account.move'].sudo().create(move_vals)
            vals['move_id'] = move.id

        return super().create(vals_list)

    def unlink(self):
        for record in self:
            if record.state == 'posted':
                raise UserError(_("You cannot delete a Cash Bank record that is in Posted state."))
        return super().unlink()

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement'

#     # === Bank/Cash Integration ===
    flag = fields.Selection([
        ('Bank Masuk', 'Bank Masuk'),
        ('Alokasi Bank Masuk INS Corp', 'Alokasi Bank Masuk INS Corp'),
        ('Alokasi Bank Masuk Umum', 'Alokasi Bank Masuk Umum')
    ], string="Flag")

    cash_bank_id = fields.Many2one('cash.bank', string="Cash Bank")
    account_periode_id = fields.Many2one(
        'acc.periode.closing',
        related='cash_bank_id.account_periode_id',
        store=True
    )

    # === Transactional Info ===
    no_bank_masuk = fields.Char(string="No Bank Masuk")
    tgl_bank_masuk = fields.Date(string="Tanggal Bank Masuk")
    amount_bank_masuk = fields.Char(string="Amount Bank Masuk")  # You can switch to Monetary/Float if needed
    balance = fields.Monetary(string="Amount", default=0, currency_field='currency_id')

    no_alokasi = fields.Char(string="No Alokasi")
    tgl_alokasi = fields.Char(string="Tanggal Alokasi")
    tgl_transaksi_alokasi = fields.Date(string="Tanggal Transaksi Alokasi")
    jumlah_alokasi = fields.Char(string="Jumlah Alokasi")  # consider Float/Monetary
    amount_tagihan = fields.Monetary(string="Amount Tagihan", currency_field='currency_id')
    nama_bank = fields.Char(string="Nama Bank")
    notes = fields.Char(string="Notes")
    keterangan = fields.Char(string="Keterangan")
    status = fields.Char(string="Status")
    status_transaksi = fields.Char(string="Status Transaksi")
    populated_time = fields.Datetime(string="Populated Time", default=lambda self: fields.Datetime.now())
    populated_date = fields.Date(
        string="Populated Date",
        compute='_compute_populated_date',
        store=True
    )
    currency_id = fields.Many2one('res.currency', string='Mata Uang', related='cash_bank_id.currency_id', store=True)
    transaction_no = fields.Char(related='account_move_id.transaction_no', store=True)
    odoo_transaction_no = fields.Char(string="Odoo Transaction No")
    transaction_date = fields.Datetime(string="Transaction Date")

    # === Relational ===
    partner_id = fields.Many2one('ajp.res.partner',string="Cust/Penjamin", tracking=True)
    partner_name = fields.Char(related="partner_id.display_name", store=True)
    account_move_id = fields.Many2one('account.move', string="Journal Entry")
    no_invoice = fields.Char(related='account_move_id.invoice_no', store=True)
    amount_invoice = fields.Monetary(related='account_move_id.amount_total_signed', store=True, currency_field='currency_id')

    no_tag_klaim = fields.Char(string="No Tagihan Klaim")
    no_fpk_ref_doc = fields.Char(string="No FPK Ref Doc")

    doc_rev = fields.Char(string="Doc Revision")
    is_uar = fields.Boolean('UAR ?', default=False)
    is_revisi = fields.Boolean('Is Revisi?')
    revision_count = fields.Char(string="Revision Count")

    date = fields.Date(
        compute='_compute_date_index',
        inverse='_inverse_date',
        store=True,
        index=True,
    )

    # === SQL Constraint ===
    _sql_constraints = [
        (
            'unique_cash_bank_line',
            'unique(name, account_periode_id, cash_bank_id)',
            'Cash Bank statement line must be unique for the period.'
        )
    ]

    # === COMPUTE METHODS ===
    @api.depends('populated_time')
    def _compute_populated_date(self):
        for rec in self:
            rec.populated_date = rec.populated_time.date() if rec.populated_time else False

    @api.depends('transaction_date')
    def _compute_date_index(self):
        for line in self:
            line.date = line.transaction_date.date() if line.transaction_date else False

    def _inverse_date(self):
        # Placeholder: nothing needed unless you want to assign something from `date`
        pass
        