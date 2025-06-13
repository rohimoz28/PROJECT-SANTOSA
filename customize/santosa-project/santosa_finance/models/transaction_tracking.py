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
    jenis_tracking = fields.Integer()
    description = fields.Char()
    beginning_balance = fields.Monetary()
    amount_debit = fields.Monetary()
    amount_credit = fields.Monetary()
    ending_balance = fields.Monetary()
    journal_number = fields.Char()
    partner_id = fields.Many2one('res.partner')
    account_move_id = fields.Many2one('account.move')
    currency_id = fields.Many2one('res.currency', string="Currency")
    offset_id = fields.Many2one('account.move')
    offset_amt = fields.Monetary()

    klaim_id = fields.Many2one('ar.klaim')
    klaim_amt = fields.Monetary()
    
    def ambil_view(self):
        self.ensure_one()  # Ensure this method is called on a single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        target_url = f"{base_url}/web#id={self.account_move_id.id}&model=account.move&view_type=form"
        print(target_url)
        if self.account_move_id:
            return {
                'type': 'ir.actions.act_url',
                'url': target_url,
                'target': 'self',
            }
        else:
            raise ValidationError("Account Move ID Belum Terisi!!!")

    def ambil_view_klaim(self):
        self.ensure_one()  # Ensure this method is called on a single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        target_url = f"{base_url}/web#id={self.klaim_id.id}&model=ar.klaim&view_type=form"
        print(target_url)
        if self.klaim_id:
            return {
                'type': 'ir.actions.act_url',
                'url': target_url,
                'target': 'self',
            }
        else:
            raise ValidationError("Klaim !!!")


    @api.depends('transaction_no', 'document_no')
    def _compute_display_name(self):
        for emp in self:
            name = ''
            context = self.env.context
            module_name = context.get('module', 'Default Module')
            if module_name != 'hr.tmsentry.summary':
                if emp.transaction_no and emp.document_no:
                    name = '[' + emp.transaction_no + '] ' + emp.document_no
                emp.display_name = name
            else:
                emp.display_name = emp.document_no
                
    def ambil_view_klaim(self):
        self.ensure_one()  # Ensure this method is called on a single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        target_url = f"{base_url}/web#id={self.account_move_id.id}&model=ar.klaim&view_type=form"
        print(target_url)
        if self.klaim_id:
            return {
                'type': 'ir.actions.act_url',
                'url': target_url,
                'target': 'self',
            }