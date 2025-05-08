# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class Report(models.Model):
    _name = 'santosa_finance.report' # name_of_module.name_of_class
    #_rec_name = 'recurring_id'
    _description = 'Report Jurnal' # Some note of table
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Header
    sales_point = fields.Char()
    journal_type = fields.Char()
    status_invoice = fields.Char()
    guarantor = fields.Char()
    no_trx = fields.Char()
    account_move_id = fields.Many2one('account.move')
    ar_in_transit = fields.Float()
    sales = fields.Float()
    alloc = fields.Float()
    other_service = fields.Float()
    sales_discount = fields.Float()
    total_invoice = fields.Float()
    ppn = fields.Float()
    medic = fields.Float()
    medicine = fields.Float()
    date = fields.Date()
    entered_date = fields.Date()
    balance = fields.Float()
    no_invoice = fields.Char(string='No. Invoice')

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