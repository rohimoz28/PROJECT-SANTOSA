# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class UploadBahv(models.Model):
    _name = 'upload.bahv'
    _description = 'Upload BAHV'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', related="nama_pasien",store=True)
    # company_id = fields.Many2one('res.company','Company', default=lambda self:self.env.company, store=True)
    branch_id = fields.Many2one('res.branch','Bisnis Unit', default=lambda self:self.env.user.branch_id, store=True)
    accounting_periode_id = fields.Many2one('acc.periode.closing','Accounting Period',store=True)
    currency_id = fields.Many2one('res.currency',
        string='Currency',
        default=12,
        store=True)
    kode_rs = fields.Char(string='Kode RS')
    kelas_rs = fields.Char(string='Kelas RS')
    kelas_rawat = fields.Char(string='Kelas Rawat')
    kode_tarif = fields.Text(string='Kode Tarif')
    ptd = fields.Char(string='PTD')
    admission_date = fields.Date(string='Admission Date')
    discharge_date = fields.Date(string='Discharge Date')
    birth_date = fields.Date(string='Birth Date')
    birth_weight = fields.Integer(string='Birth Weight')
    sex = fields.Selection([('1',"Male"),('2',"Female")],string='Sex')
    discharge_status = fields.Char(string='Discharge Status')
    admission_date_str = fields.Char(compute="_compute_admission_date_str", store=True)
    discharge_date_str = fields.Char(compute="_compute_admission_date_str", store=True)
    
    @api.depends('admission_date','discharge_date')
    def _compute_admission_date_str(self):
        for rec in self:
            rec.admission_date_str = rec.admission_date.strftime('%d-%B-%y') if rec.admission_date else ''
            rec.discharge_date_str = rec.discharge_date.strftime('%d-%B-%Y') if rec.discharge_date else ''
    
    
    diaglist = fields.Char(string='Diaglist')
    proclist = fields.Char(string='Proclist')
    adl1 = fields.Char(string='ADL1')
    adl2 = fields.Char(string='ADL2')
    in_sp = fields.Char(string='IN SP')
    in_sr = fields.Char(string='IN SR')
    in_si = fields.Char(string='IN SI')
    in_sd = fields.Char(string='IN SD')
    inacbg = fields.Char(string='INACBG')
    subacute = fields.Text(string='Subacute')
    chronic = fields.Text(string='Chronic')
    sp = fields.Char(string='SP')
    sr = fields.Char(string='SR')
    si = fields.Char(string='SI')
    sd = fields.Char(string='SD')
    deskripsi_inacbg = fields.Char(string='Deskripsi INACBG')
    tarif_inacbg = fields.Monetary(string='Tarif INACBG')
    tarif_subacute = fields.Monetary(string='Tarif Subacute')
    tarif_chronic = fields.Monetary(string='Tarif Chronic')
    deskripsi_sp = fields.Char(string='Deskripsi SP')
    tarif_sp = fields.Monetary(string='Tarif SP')
    deskripsi_sr = fields.Char(string='Deskripsi SR')
    tarif_sr = fields.Monetary(string='Tarif SR')
    deskripsi_si = fields.Char(string='Deskripsi SI')
    tarif_si = fields.Monetary(string='Tarif SI')
    deskripsi_sd = fields.Text(string='Deskripsi SD')
    tarif_sd = fields.Monetary(string='Tarif SD')
    total_tarif = fields.Monetary(string='Total Tarif')
    tarif_rs = fields.Monetary(string='Tarif RS')
    tarif_poli_eks = fields.Monetary(string='Tarif Poli Eks')
    los = fields.Integer(string='LOS')
    icu_indikator = fields.Char(string='ICU Indikator')
    icu_los = fields.Char(string='ICU LOS')
    vent_hour = fields.Integer(string='Vent Hour')
    nama_pasien = fields.Char(string='Nama Pasien')
    mrn = fields.Char(string='MRN')
    umur_tahun = fields.Integer(string='Umur Tahun')
    umur_bulan = fields.Integer(string='Umur Bulanpayor_')
    umur_hari = fields.Integer(string='Umur Hari')
    dpjp = fields.Char(string='DPJP')
    sep = fields.Char(string='SEP')
    nokartu = fields.Char(string='No Kartu')
    payor_id = fields.Char(string='Payor ID')
    coder_id = fields.Char(string='Coder ID')
    versi_inacbg = fields.Char(string='Versi INACBG')
    versi_grouper = fields.Char(string='Versi Grouper')
    c1 = fields.Text(string='C1')
    c2 = fields.Text(string='C2')
    c3 = fields.Text(string='C3')
    c4 = fields.Text(string='C4')
    prosedur_non_bedah = fields.Monetary(string='Prosedur Non Bedah')
    prosedur_bedah = fields.Monetary(string='Prosedur Bedah')
    konsultasi = fields.Monetary(string='Konsultasi')
    tenaga_ahli = fields.Monetary(string='Tenaga Ahli')
    keperawatan = fields.Monetary(string='Keperawatan')
    penunjang = fields.Monetary(string='Penunjang')
    radiologi = fields.Monetary(string='Radiologi')
    laboratorium = fields.Monetary(string='Laboratorium')
    pelayanan_darah = fields.Monetary(string='Pelayanan Darah')
    rehabilitasi = fields.Monetary(string='Rehabilitasi')
    kamar_akomodasi = fields.Monetary(string='Kamar Akomodasi')
    rawat_intensif = fields.Monetary(string='Rawat Intensif')
    obat = fields.Monetary(string='Obat')
    alkes = fields.Monetary(string='Alkes')
    bmhp = fields.Monetary(string='BMHP')
    sewa_alat = fields.Monetary(string='Sewa Alat')
    obat_kronis = fields.Monetary(string='Obat Kronis')
    obat_kemo = fields.Monetary(string='Obat Kemo')
    file_name = fields.Char(string='File Name')
