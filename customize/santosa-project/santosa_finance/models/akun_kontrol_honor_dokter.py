# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Akun_kontrol_honor_dokter(models.Model):
    _name = 'santosa_finance.akun_kontrol_honor_dokter'
    _description = 'Akun Kontrol Honor Dokter'

    name = fields.Char('Name')
    idTrx = fields.Integer()
    TrxDate = fields.Date('Tanggal TRX',related='invoice_id.invoice_date', store=True)
    TrxNo = fields.Char('Nomor TRX',related='invoice_id.name', store=True)
    Invoice_date = fields.Date('Tanggal Invoice',related='invoice_id.invoice_date' , store=True)
    Invoice_No = fields.Char('Nomor Invoice',related='invoice_id.temp_invoice_no', store=True)
    PenjaminName = fields.Char('Nama Penjamin', related='invoice_id.penjamin_name_id.name' , store=True)
    Penjaminid = fields.Many2one('res.partner','Nama Penjamin', related='invoice_id.penjamin_name_id', store=True)
    PiutangUsaha = fields.Float('Piutang Usaha')
    NoTrxKlaim = fields.Char('Nomor Klaim')
    PiutangKlaim = fields.Float('Piutang Klaim')
    TolakanKlaim = fields.Float('Tolakan Klaim')
    FeeDokter = fields.Float('Fee Dokter')
    KlaimdiBayar = fields.Float('Klaim di bayar')
    BebanBiaya = fields.Float('Beban Biaya')
    invoice_id = fields.Many2one('account.move')
    partner_id = fields.Many2one('res.partner', related='invoice_id.partner_id')
    
    def ambil_view(self):
        self.ensure_one()  # Ensure this method is called on a single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        target_url = f"{base_url}/web#id={self.invoice_id.id}&model=account.move&view_type=form"
        # print(target_url)
        if self.account_move_id:
            return {
                'type': 'ir.actions.act_url',
                'url': target_url,
                'target': 'self',
            }
        else:
            raise ValidationError("Invoice Belum Terisi!!!")
        
    def unlink(self):
        return super(Akun_kontrol_honor_dokter, self).unlink()
                
    def open_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("No invoice linked to this record."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }