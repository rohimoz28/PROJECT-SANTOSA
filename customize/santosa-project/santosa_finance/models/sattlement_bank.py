from odoo import models, fields, api, tools, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class SattlementBank(models.Model):
    _name = 'ajp.sattlement.bank'
    _description = 'Sattlement Bank'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    number = fields.Char(string='Sattlement Number', required=True, copy=False,)
    date = fields.Date(string='Sattlement Date', default=fields.Date.context_today, track_visibility='onchange')
    accounting_period = fields.Many2one(
        'acc.periode.closing',
        string="Accounting Periode",
        domain="[('state_process', '=', 'running'),('branch_id', '=',branch_id)]",
        default=lambda self: self._get_running_periode(),required=True
    )
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        required=True, 
        default=lambda self: self.env.user.company_id.currency_id
    )
    branch_id = fields.Many2one('res.branch', string='Branch', 
                                track_visibility='onchange', 
                                default=lambda self: self.env.user.branch_id.id)
    bank_type = fields.Selection([
        ('ar klaim', 'Ar Klaim'),
        ('pelayanan', 'Ar Pelayanan'),
        ('non pelayanan', 'AR Non Pelayanan')], 
        string='Bank Type', track_visibility='onchange')
    sattlement_source = fields.Selection([
        ('ump', 'UMP'),
        ('adm bank', 'Biaya Admin Bank'),
        ('tax', 'Biaya Pajak'),
        ('audit', 'Biaya Audit'),],
        string='Sattlement Source', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    sattlement_amount = fields.Monetary(string='Settlement Amount', currency_field='currency_id', track_visibility='onchange')
    description = fields.Text(string='Description', track_visibility='onchange')
    ajp_sattlement_bank_line_ids = fields.One2many('ajp.sattlement.bank.line', 'sattlement_bank_id', string='Sattlement Bank Line', track_visibility='onchange')
    bank_masuk_ids = fields.One2many('ajp.sattlement.bank.ump', 'sattlement_bank_id', string='Sattlement Bank UMP Line', track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')], 
        string='Status', readonly=True, default='draft', track_visibility='onchange')

    # UTILITY METHOD
    def _get_running_periode(self):
        periode = self.env['acc.periode.closing'].search([
            ('state_process', '=', 'running'),
            ('branch_id', '=', self.env.user.branch_id.id),
            ('open_periode_from', '<=', fields.Datetime.now()),
            ('open_periode_to', '>=', fields.Datetime.now())
        ], order='open_periode_to desc', limit=1)
        return periode
    
    
    #     #Function For PopUp Search Employee
    # def action_search_employee(self):
    #     wizard = self.env['hr.wizard.settlement.bank'].create({
    #                 'branch_id':self.branch_id.id,
    #                 'partner_id':self.partner_id.id,
    #                 'accounting_period':self.accounting_period.id,
    #                 })
    #     emp_line = self.env['wizard.settlement.bank.list'].search([('wiz_settle_bank_id','=',wizard.id)])
    #     if not emp_line:
    #         wizard._isi_employee()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Search Bank Masuk/Invoice AR'),
    #         'res_model': 'hr.wizard.settlement.bank',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'res_id': wizard.id,
    #         'domain': [('branch_id', '=', self.branch_id.id),('partner_id', '=', self.partner_id.id),('accounting_period', '=', self.accounting_period.id)],
    #         'views': [[False, 'form']]
    #     }
    
    def action_search_bank_masuk(self):
        if not self.accounting_period.id:
            raise UserError(_("Please fill Accounting Period"))
        if not self.partner_id.id:
            raise UserError(_("Please fill Partner"))
        wizard = self.env['wizard.settlement.bank'].create({
                    'sattlement_bank_id':self.id,})
        emp_line = self.env['wizard.settlement.bank.list'].search([('wiz_settle_bank_id','=',wizard.id)])
        if not emp_line:
            wizard._isi_employee()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Search Bank Masuk/Invoice AR'),
            'res_model': 'wizard.settlement.bank',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard.id,
            'views': [[False, 'form']]
        }
    
    def action_search_bank_inv_ar(self):
        pass
    
    def act_post(self):
        pass

    def act_cancel(self):
        pass

class SattlementBankLine(models.Model):
    _name = 'ajp.sattlement.bank.line'
    _description = 'Sattlement Bank Detail'

    sattlement_bank_id = fields.Many2one('ajp.sattlement.bank', string='Sattlement Bank')        
    state = fields.Selection(related='sattlement_bank_id.state',
        string='Status', readonly=True, store=True)
    currency_id = fields.Many2one(related='sattlement_bank_id.currency_id',)
    claim_date = fields.Date(string='Claim Date', track_visibility='onchange')
    claim_number = fields.Char(string='Claim Number', track_visibility='onchange')
    trx_date = fields.Date(string='Invoice Date')
    trx_number = fields.Many2one('account.move', string='Invoice Date')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_number = fields.Char(string='Invoice Number')
    invoice_claim_amount = fields.Monetary(string='Invoice/Claim Amount', currency_field='currency_id')
    outstanding_inv_amount = fields.Monetary(string='Outstanding Inv/Claim Amount', currency_field='currency_id')
    payment_inv_amount = fields.Monetary(string='Payment Inv/Claim Amount', currency_field='currency_id')
    ending_balance = fields.Monetary(string='Amount Ending Balance', currency_field='currency_id')

class SattlementBankUMP(models.Model):
    _name = 'ajp.sattlement.bank.ump'
    _description = 'Sattlement Bank UMP'

    sattlement_bank_id = fields.Many2one('ajp.sattlement.bank', string='Sattlement Bank')        
    state = fields.Selection(related='sattlement_bank_id.state',
        string='Status', readonly=True, store=True)
    partner_id = fields.Many2one('res.partner',string="Cust/Penjamin", tracking=True)
    ajp_partner_id = fields.Many2one('ajp.res.partner',string="Cust/Penjamin", tracking=True)
    cash_bank_id = fields.Many2one('cash.bank', string="Cash Bank")
    currency_id = fields.Many2one(related='sattlement_bank_id.currency_id',)
    name = fields.Char(string='Name', track_visibility='onchange')
    ump_id = fields.Many2one('cash.bank', string="Bank Masuk") 
    amount_ump = fields.Monetary(string='Total UMP', currency_field='currency_id')
    residual_ump = fields.Monetary(string='Residual UMP', currency_field='currency_id')
    total_ump = fields.Monetary(string='Total UMP', currency_field='currency_id')
    amount_bm = fields.Monetary(string='Amount BM', currency_field='currency_id')
