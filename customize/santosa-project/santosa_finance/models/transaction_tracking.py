# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError



class TransactionTracking(models.Model):
    _name = 'santosa_finance.transaction_tracking' # name_of_module.name_of_class
    _rec_name = 'odoo_transaction_no'
    _description = 'Transaction Tracking' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    transaction_date = fields.Date()
    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()
    document_date = fields.Date()
    populate_date = fields.Date()
    entered_date = fields.Date()
    document_no = fields.Char()
    transaction_class = fields.Char()
    jenis = fields.Integer()
    flag = fields.Integer()
    jenis_tracking = fields.Integer()
    description = fields.Char()
    beginning_balance = fields.Monetary(compute='calculate_ending_balance', store=True)
    amount_debit = fields.Monetary(default=0.00)
    amount_credit = fields.Monetary(default=0.00)
    ending_balance = fields.Monetary(compute='calculate_ending_balance', store=True)
    journal_number = fields.Char()
    partner_id = fields.Many2one('res.partner')
    account_move_id = fields.Many2one('account.move')
    currency_id = fields.Many2one('res.currency', string="Currency")
    offset_id = fields.Many2one('account.move')
    offset_amt = fields.Monetary()
    accounting_periode_id = fields.Many2one('acc.periode.closing','Accounting Period', required=True, domain="[('state_process', '=', 'running'),('branch_id', '=',branch_id)]", 
        default=lambda self: self._get_last_open_periode()
    )

    @api.model
    def _get_last_open_periode(self):
        periode = self.env['acc.periode.closing'].search(
            [
                ('state_process', '=', 'running'),
                ('branch_id', '=', self.env.user.branch_id.id),
                ('open_periode_from', '<', fields.Datetime.now()),
                ('open_periode_to', '>', fields.Datetime.now())
            ],
            order='open_periode_to desc',
            limit=1
        )
        return periode.id if periode else False

    def ambil_view(self):
        self.ensure_one()  # Ensure this method is called on a single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        target_url = f"{base_url}/web#id={self.account_move_id.id}&model=account.move&view_type=form"
        if self.account_move_id:
            return {
                'type': 'ir.actions.act_url',
                'url': target_url,
                'target': 'self',
            }
        else:
            raise ValidationError("Account Move ID Belum Terisi!!!")
        
    def calculate_ending_balance(self):
        for line in self:
            get_last_trans = self.env['santosa_finance.transaction_tracking'].search([('partner_id','=',line.partner_id.id),('flag','=',line.flag)], order='id desc', limit=1)
            if get_last_trans:
                line.beginning_balance = get_last_trans.ending_balance or 0.00
            else:
                line.beginning_balance = 0.00
            if line.beginning_balance and line.amount_debit and line.amount_credit:
                line.ending_balance = line.beginning_balance + line.amount_debit - line.amount_credit
            else:
                line.ending_balance=0.00

    # @api.depends('transaction_no', 'document_no')
    # def _compute_display_name(self):
    #     for emp in self:
    #         name = ''
    #         context = self.env.context
    #         module_name = context.get('module', 'Default Module')
    #         if module_name != 'hr.tmsentry.summary':
    #             if emp.transaction_no and emp.document_no:
    #                 name = '[' + emp.transaction_no + '] ' + emp.document_no
    #             emp.display_name = name
    #         else:
    #             emp.display_name = emp.document_no4