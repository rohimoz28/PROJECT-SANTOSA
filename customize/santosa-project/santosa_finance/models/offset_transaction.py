# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta


class OffsetTransaction(models.Model):
    _name = 'santosa_finance.offset_transaction' # name_of_module.name_of_class
    _rec_name = 'odoo_transaction_no'
    _description = 'Offset Transaction' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    transaction_no = fields.Char()
    odoo_transaction_no = fields.Char()
    transaction_date = fields.Date()
    offset_no = fields.Char()
    offset_date = fields.Date()
    offset_type = fields.Selection([ 
        ('Biaya Admin Bank', 'Biaya Admin Bank'),
        ('Biaya Pajak', 'Biaya Pajak'),
        ('Biaya Audit', 'Biaya Audit'),
        ('Write Off', 'Write Off')
    ])
    offset_description = fields.Char()
    currency_id = fields.Many2one('res.currency', string="Currency")
    document_ref_number = fields.Char()
    attachment_document_ref = fields.Binary() 
    total_amount_offset = fields.Float()
    partner_id = fields.Many2one('res.partner')
    remarks = fields.Char()
    status_transaksi = fields.Char()
    periode_number = fields.Char()
    periode_closing_date = fields.Date()
    line_ids = fields.One2many('santosa_finance.offset_transaction_details','order_id')
    
    @api.onchange('line_ids.offset_amt')
    def _real_all_pick(self):
        for order in self:
            amount_untaxed = 0.0
            if order.line_ids:
                amount_untaxed = sum(self.mapped('line_ids').mapped('offset_amt'))    
            order.total_amount_offset = amount_untaxed

class OffsetTransactionDetails(models.Model):
    _name = 'santosa_finance.offset_transaction_details' # name_of_module.name_of_class
    _rec_name = 'offset_number'
    _description = 'Offset Transaction' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    # test = fields.Selection(selection=lambda self: self._get_dynamic_selection(),
    #     string="Dynamic Selection")
    
    order_id = fields.Many2one(string='Header', comodel_name='santosa_finance.offset_transaction', ondelete='restrict')
    trx_id = fields.Many2one('santosa_finance.transaction_tracking', domain="[('partner_id', '=',partner_id)]", string="Transaction Tracking")
    offset_number = fields.Char(related='order_id.offset_no')
    #doc = fields.Char() masih nunggu dokumen fsd untuk detailnya harus gimana
    doc_date = fields.Date()
    doc_amount = fields.Float()
    remarks = fields.Char()
    transaction_date = fields.Date(related='trx_id.transaction_date')
    transaction_no = fields.Char(related='trx_id.transaction_no')
    odoo_transaction_no = fields.Char(related='trx_id.odoo_transaction_no')
    document_date = fields.Date(related='trx_id.document_date')
    document_no = fields.Char(related='trx_id.document_no')
    description = fields.Char(related='trx_id.description')
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id',store=True)
    currency_id = fields.Many2one('res.currency', string="Currency",related='order_id.currency_id')
    beginning_balance = fields.Monetary(related='trx_id.beginning_balance')
    amount_debit = fields.Monetary(related='trx_id.amount_debit')
    amount_credit = fields.Monetary(related='trx_id.amount_credit')
    ending_balance = fields.Monetary(related='trx_id.ending_balance')
    account_move_id = fields.Many2one('account.move',related='trx_id.account_move_id')
    offset_amt = fields.Monetary()


    # def _get_dynamic_selection(self):
    #     query =""" select id,concat('[',transaction_no,'] ',document_no) document_no from santosa_finance_transaction_tracking
    #     """
    #     self.env.cr.execute(query)
    #     trx = self.env.cr.fetchall()
    #     return [(country[0], country[1]) for country in trx]
    
    