from odoo import models, fields, api, tools, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError

class wizard_settlement_bank(models.TransientModel):
    _name = 'wizard.settlement.bank'
    _description = 'Wizard Settlement Bank'
    
    sattlement_bank_id = fields.Many2one('ajp.sattlement.bank', string='Sattlement Bank')
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('wizard.settlement.bank.list', 'wiz_settle_bank_id', string='Settlement Bank Lines')

    @api.model
    def default_get(self, fields):
        result = super(wizard_settlement_bank, self).default_get(fields)
        myempg = self._context.get('active_id')
        settlement_bank = self.env['ajp.sattlement.bank'].browse(myempg).id
        if settlement_bank:
            result[sattlement_bank_id] = settlement_bank
        return result

    @api.onchange('start_date', 'end_date', )
    def _get_filtered_employees_domain(self):
        if self.start_date > self.end_date:
            raise UserError(_("Start Date cannot be greater than End Date."))
        domain = [('status', '=', 'posted'),('is_uar','!=',True).
                  ('distributed_state', '!=', 'full'),
                  ('branch_id', '=', self.sattlement_bank_id.branch_id.id),
                  ('partner_id', '=', self.sattlement_bank_id.partner_id.id),
                  ('account_periode_id', '=', self.sattlement_bank_id.accounting_period.id)]
        if self.start_date and self.end_date and self.sattlement_bank_id.accounting_period.open_periode_from and self.sattlement_bank_id.accounting_period.open_periode_to:
            # if self.start_date < self.sattlement_bank_id.accounting_period.open_periode_from or self.end_date < self.sattlement_bank_id.accounting_period.open_periode_from or self.start_date > self.sattlement_bank_id.accounting_period.open_periode_to or self.end_date > self.sattlement_bank_id.accounting_period.open_periode_to :
            #     raise UserError(_("Date must be within the selected Accounting Period."))
            if self.start_date:
                domain.append(('date', '>', self.start_date))
            if self.end_date:
                domain.append(('date', '<', self.end_date))
        return domain

    def btn_select_all(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.write({'is_select': True})
    
    def _isi_employee(self):
        for rec in self:
            rec.line_ids = [(5, 0, 0)]
            domain = rec._get_filtered_employees_domain()
            statement_detail = self.env['account.bank.statement'].search(domain)
            datadetails = self.env['wizard.settlement.bank.list']
            if statement_detail:
                for lines in statement_detail:
                    datadetails.sudo().create({
                        'wiz_settle_bank_id': lines.id,
                        'cash_bank_id': lines.cash_bank_id.id,
                        'no_trs': lines.name,
                        'date_trx': lines.date,
                        'partner_id': lines.partner_id.id,
                        'tgl_bank_masuk': lines.date,
                        'balance': lines.balance,
                        'residual_ump': lines.residual_ump,
                        'is_select': False,
                    })

    def act_apply(self):
        for rec in self:
            selected_lines = rec.line_ids.filtered(lambda line: line.is_select)
            if not selected_lines:
                raise UserError(_("Please select at least one line to apply settlement."))
            for line in selected_lines:
                if rec.sattlement_bank_id.sattlement_source == 'ump':
                    if line.residual_ump <= 0:
                        raise UserError(_("The selected transaction %s has no remaining UMP to settle.") % line.no_trs)
                    if rec.sattlement_bank_id.amount_bm <= 0:
                        raise UserError(_("The Settlement Bank amount must be greater than zero."))
                    if rec.sattlement_bank_id.amount_bm > line.residual_ump:
                        raise UserError(_("The Settlement Bank amount cannot exceed the residual UMP of the selected transaction %s.") % line.no_trs)
                    # Update the residual_ump in account.bank.statement
                    line.residual_ump -= rec.sattlement_bank_id.amount_bm
                    # Create a link between settlement bank and bank statement
                    rec.sattlement_bank_id.bank_masuk_ids = [(4, line.id)]
            rec.sattlement_bank_id.state = 'done'
        return {'type': 'ir.actions.act_window_close'}
    
class wizard_settlement_bank_list(models.TransientModel):
    _name = 'wizard.settlement.bank.list'
    _description = 'Wizard Settlement Bank List'
    
    wiz_settle_bank_id = fields.Many2one('wizard.settlement.bank', string='Wizard Settlement Bank', required=True)
    cash_bank_id = fields.Many2one('cash.bank', string="Cash Bank")
    no_trs = fields.Char(string='Transaction No')
    date_trx = fields.Date(string='Date')
    partner_id = fields.Many2one(string='Penjamin', comodel_name='res.partner')
    no_bank_masuk = fields.Char(string="No Bank Masuk")
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
    tgl_bank_masuk = fields.Date(string="Tanggal Bank Masuk")
    is_select = fields.Boolean(string='Select', default=False)
    balance = fields.Monetary(string="Amount", tracking=True, store=True)
    residual_ump = fields.Monetary(string="Residual UMP", tracking=True, store=True)

                           

    # date_from = fields.Date(string='Date From', required=True, default=fields.Date.context_today)
    # date_to = fields.Date(string='Date To', required=True, default=fields.Date.context_today)
    # partner_id = fields.Many2one('res.partner', string='Partner')
    # accounting_period = fields.Many2one(
    #     'acc.periode.closing',
    #     string="Accounting Periode",
    #     domain="[('state_process', '=', 'running'),('branch_id', '=',branch_id)]",
    #     default=lambda self: self._get_running_periode()
    # )

    # def action_search(self):
    #     domain = []
    #     if self.partner_id:
    #         domain.append(('partner_id', '=', self.partner_id.id))
    #     if self.date_from:
    #         domain.append(('date', '>=', self.date_from))
    #     if self.date_to:
    #         domain.append(('date', '<=', self.date_to))
        
    #     records = self.env['account.move'].search(domain)
    #     return {
    #         'name': _('Search Results'),
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'type': 'ir.actions.act_window',
    #         'domain': domain,
    #         'context': {'create': False}
    #     }