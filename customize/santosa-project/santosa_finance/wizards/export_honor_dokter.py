import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
# import base64, BytesIO, xlsxwriter are not used directly here

_logger = logging.getLogger(__name__)


class ExportHonorDokter(models.TransientModel):
    _name = 'export.honor.dokter'
    _description = _('Export Honor Dokter')

    # penjamin_id = fields.Many2one('res.partner', string="Penjamin", domain="[('id', 'in', allowed_penjamin_ids)]")
    penjamin_id = fields.Many2one('res.partner', string="Penjamin")
    allowed_penjamin_ids = fields.Many2many('res.partner', compute='_compute_allowed_penjamin_ids')
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    
    def _compute_allowed_penjamin_ids(self):
        for wizard in self:
            penjamins = self.env['santosa_finance.akun_kontrol_honor_dokter'].search([]).mapped('Penjaminid')
            wizard.allowed_penjamin_ids = penjamins

    @api.constrains('date_start', 'date_end')
    def _check_date_range(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start > record.date_end:
                raise UserError(_("Tanggal mulai tidak boleh lebih besar dari tanggal akhir."))

    def action_export_excel(self):
        self.ensure_one()

        domain = []
        if self.penjamin_id:
            domain.append(('Penjaminid', '=', self.penjamin_id.id))
        if self.date_start:
            domain.append(('Invoice_date', '>=', self.date_start or fields.Datetime.today()))
        if self.date_end:
            domain.append(('Invoice_date', '<=', self.date_end or fields.Datetime.today()))

        records = self.env['santosa_finance.akun_kontrol_honor_dokter'].search(domain)

        if not records:
            raise UserError(_("Tidak ada data yang ditemukan untuk kriteria pencarian."))

        return {
            'type': 'ir.actions.report',
            'report_name': 'santosa_finance.rekap_honor_docter_xlsx',
            'report_type': 'xlsx',
            'report_file': f'Rekap_honor_dokter_{self.penjamin_id.name or "All"}',
            'context': {
                'active_model': 'santosa_finance.akun_kontrol_honor_dokter',
                'active_ids': records.ids,
            }
        }

    # def button_export_html(self):
    #     self.ensure_one()

    #     domain = []
    #     if self.penjamin_id:
    #         domain.append(('Penjaminid', '=', self.penjamin_id.id))
    #     if self.date_start:
    #         domain.append(('invoice_date', '>=', self.date_start or fields.Datetime.today()))
    #     if self.date_end:
    #         domain.append(('invoice_date', '<=', self.date_end or fields.Datetime.today()))

    #     records = self.env['santosa_finance.akun_kontrol_honor_dokter'].search(domain)

    #     if not records:
    #         raise UserError(_("Tidak ada data yang ditemukan untuk kriteria pencarian."))

    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': 'santosa_finance.rekap_honor_docter_html',
    #         'report_type': 'qweb-html',
    #         'report_file': f'Rekap_honor_dokter_{self.penjamin_id.name or "All"}',
    #         'context': {
    #             'active_model': 'santosa_finance.akun_kontrol_honor_dokter',
    #             'active_ids': records.ids,
    #         }
    #     }