from odoo import models, fields, api, _
from odoo.exceptions import UserError

class wizard_settlement_klaim(models.TransientModel):
    _name = 'wizard.settlement.klaim'
    _description = 'Wizard Settlement Klaim'
    
    sattlement_bank_id = fields.Many2one('ajp.sattlement.bank', string='Sattlement Klaim')
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('wizard.settlement.klaim.list', 'wiz_settle_klaim_id', string='Settlement Klaim Lines')

    @api.onchange('start_date', 'end_date')
    def _check_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise UserError(_("Start Date cannot be greater than End Date."))

    def _isi_klaim(self):
        for rec in self:
            rec.line_ids = [(5, 0, 0)]  # Clear existing lines
            
            if not (rec.sattlement_bank_id and rec.start_date and rec.end_date):
                continue
            
            domain = [
                ('state', '=', 'posted'),
                ('partner_id', '=', rec.sattlement_bank_id.partner_id.id),
                ('date', '>=', rec.start_date),
                ('date', '<=', rec.end_date),
                ('amount_residual', '>', 0),
            ]
            klaims = self.env['account.move'].search(domain)
            lines_vals = []
            for klaim in klaims:
                lines_vals.append({
                    'wiz_settle_bank_id': rec.id,
                    'klaim_id': klaim.id,
                    'klaim_date': klaim.date,
                    'amount': klaim.amount_total,
                    'residual_amount': klaim.amount_residual,
                    'is_select': False,
                })
            self.env['wizard.settlement.klaim.list'].sudo().create(lines_vals)

    def act_apply(self):
        for rec in self:
            selected_lines = rec.line_ids.filtered(lambda l: l.is_select)
            if not selected_lines:
                raise UserError(_("Please select at least one claim to apply settlement."))
            
            for line in selected_lines:
                # Example logic: mark claim as settled or reduce residual
                if line.residual_amount <= 0:
                    raise UserError(_("Claim %s has no outstanding amount.") % line.klaim_id.name)
                # Example: you could update residual here or create settlement record
                
            rec.sattlement_bank_id.state = 'done'  # Example state update

        return {'type': 'ir.actions.act_window_close'}
    
    

    def btn_select_all(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.write({'is_select': True})


class wizard_settlement_klaim_list(models.TransientModel):
    _name = 'wizard.settlement.klaim.list'
    _description = 'Wizard Settlement Klaim List'
    
    wiz_settle_klaim_id = fields.Many2one('wizard.settlement.klaim', string='Wizard Settlement klaim', required=True)
    klaim_id = fields.Many2one('account.move', string='No Klaim')
    klaim_date = fields.Date(string='Date Klaim')
    currency_id = fields.Many2one(related='klaim_id.currency_id')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    residual_amount = fields.Monetary(string='Outstanding Klaim', currency_field='currency_id')
    is_select = fields.Boolean(string='Select', default=False)
