from odoo import models, fields, api, _
from odoo.exceptions import UserError

class wizard_settlement_bank(models.TransientModel):
    _name = 'wizard.settlement.bank'
    _description = 'Wizard Settlement Bank'
    
    sattlement_bank_id = fields.Many2one('ajp.sattlement.bank', string='Sattlement Bank')
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('wizard.settlement.bank.list', 'wiz_settle_bank_id', string='Settlement Bank Lines')

    @api.model
    def default_get(self, fields_list):
        result = super(wizard_settlement_bank, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id:
            settlement_bank = self.env['ajp.sattlement.bank'].browse(active_id)
            if settlement_bank.exists():
                result['sattlement_bank_id'] = settlement_bank.id
        return result

    @api.onchange('start_date', 'end_date')
    def _get_filtered_employees_domain(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise UserError(_("Start Date cannot be greater than End Date."))

        domain = [('status', '=', 'posted'), ('is_uar', '!=', True),
                  ('distributed_state', '!=', 'full')]

        if self.sattlement_bank_id:
            domain += [
                ('branch_id', '=', self.sattlement_bank_id.branch_id.id),
                ('partner_id', '=', self.sattlement_bank_id.partner_id.id),
                ('account_periode_id', '=', self.sattlement_bank_id.accounting_period.id)
            ]

            ap = self.sattlement_bank_id.accounting_period
            if self.start_date and self.end_date and ap and ap.open_periode_from and ap.open_periode_to:
                # Uncomment if date validation within period is needed
                # if self.start_date < ap.open_periode_from or self.end_date > ap.open_periode_to:
                #     raise UserError(_("Date must be within the selected Accounting Period."))
                domain.append(('date', '>=', self.start_date))
                domain.append(('date', '<=', self.end_date))

        return domain

    def btn_select_all(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.write({'is_select': True})

    def _isi_employee(self):
        for rec in self:
            rec.line_ids = [(5, 0, 0)]  # Clear lines
            domain = rec._get_filtered_employees_domain()
            statement_detail = self.env['account.bank.statement'].search(domain)
            if statement_detail:
                lines_vals = []
                for line in statement_detail:
                    lines_vals.append({
                        'wiz_settle_bank_id': rec.id,
                        'cash_bank_id': line.cash_bank_id.id,
                        'no_trs': line.name,
                        'date_trx': line.date,
                        'partner_id': line.partner_id.id,
                        'tgl_bank_masuk': line.date,
                        'balance': line.balance,
                        'residual_ump': line.residual_ump,
                        'is_select': False,
                    })
                self.env['wizard.settlement.bank.list'].sudo().create(lines_vals)

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

                    # Update the residual_ump in wizard settlement bank list and also sync if needed
                    line.residual_ump -= rec.sattlement_bank_id.amount_bm

                    # Create a link between settlement bank and bank statement
                    rec.sattlement_bank_id.bank_masuk_ids = [(4, line.cash_bank_id.id)]  # Assuming bank_masuk_ids is Many2many or One2many to cash_bank

            rec.sattlement_bank_id.state = 'done'

        return {'type': 'ir.actions.act_window_close'}


class wizard_settlement_bank_list(models.TransientModel):
    _name = 'wizard.settlement.bank.list'
    _description = 'Wizard Settlement Bank List'
    
    wiz_settle_bank_id = fields.Many2one('wizard.settlement.bank', string='Wizard Settlement Bank', required=True)
    cash_bank_id = fields.Many2one('cash.bank', string="Cash Bank")
    no_trs = fields.Char(string='Transaction No')
    date_trx = fields.Date(string='Date')
    partner_id = fields.Many2one('res.partner', string='Penjamin')
    no_bank_masuk = fields.Char(string="No Bank Masuk")
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    tgl_bank_masuk = fields.Date(string="Tanggal Bank Masuk")
    is_select = fields.Boolean(string='Select', default=False)
    balance = fields.Monetary(string="Amount")
    residual_ump = fields.Monetary(string="Residual UMP")
