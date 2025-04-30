# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

import datetime

def addYears(date, years):
    if not date:
        return 0
    result = date + datetime.timedelta(366 * years)
    if years > 0:
        while result.year - date.year > years or date.month < result.month or date.day < result.day:
            result += datetime.timedelta(-1)
    elif years < 0:
        while result.year - date.year < years or date.month > result.month or date.day > result.day:
            result += datetime.timedelta(1)
    return result

class HREmployee(models.Model):
    _inherit = "hr.employee"


    periode_probation = fields.Integer('Masa percobaan',default=3,readonly="job_status != 'permanent'")
    ext_probation = fields.Integer('Perpanjangan Percobaan',readonly="job_status != 'permanent'")
    confirm_probation = fields.Date('Tanggal Terkonfirmasi',compute='hitung_confirmation',store=False,readonly=False)
    retire_age = fields.Integer('Usia Pensiun',default=55)
    pension_date = fields.Date('Tanggal Pensiun',compute='_isi_pensiunemployee',store=False,readonly=False)
    bond_service = fields.Boolean('Ikatan Kontrak',default=False)
    service_from = fields.Date('Kontrak Mulai')
    service_to = fields.Date('Kontrak Hingga')
    is_pinalty = fields.Boolean('Penalti',default=False)
    pinalty_bs = fields.Integer('Penalti BS')

    pinalty_amount = fields.Monetary('Jumlah Pinalti')
    resign_notice = fields.Integer('Masa pengunduran diri')
    asset_ids = fields.One2many('hr.employee.assets','employee_id',auto_join=True,string='Detail Asset')


    @api.depends('join_date','periode_probation')
    def hitung_confirmation(self):
        for allrec in self:
            if allrec.periode_probation and allrec.join_date:
                allrec.confirm_probation = allrec.join_date + relativedelta(months=+allrec.periode_probation)
            elif allrec.periode_probation and not allrec.join_date:
                allrec.confirm_probation = False
            elif not allrec.periode_probation and not allrec.join_date:
                allrec.confirm_probation = False
            else:
                if allrec.join_date:
                    allrec.confirm_probation = allrec.join_date
                else:
                    allrec.confirm_probation = False

    @api.depends('retire_age','state','birthday')
    def _isi_pensiunemployee(self):
        for alldatarec in self:
            if not alldatarec.retire_age:
                alldatarec.pension_date = False
            else:
                usiapensiun = alldatarec.retire_age
                haruspensiun = addYears(alldatarec.birthday,int(usiapensiun))
                alldatarec.pension_date = haruspensiun


class HREmployeeAssets(models.Model):
    _name = "hr.employee.assets"

    employee_id = fields.Many2one('hr.employee',string='Employee ID',index=True)
    asset_name = fields.Char('Tipe aset / Tunjangan')
    asset_number = fields.Char('Nomor Aset / Tunjangan')
    uom = fields.Many2one('uom.uom',string='UoM')
    asset_qty = fields.Float('Qty')
    received_date = fields.Date('Tanggal Diterima')
    returned_date = fields.Date('Tanggal Dikembalikan')
    keterangan = fields.Text('Keterangan')
    brand = fields.Char(string = 'Merek / Model')
    serial_number = fields.Char(string = 'Serial Number')
    no_ref = fields.Char(string = 'No Ref (No TTU)')
    product_id = fields.Many2one('product.product', string="Produk", related="product_template_id.product_variant_id", store=True)
    stock_lot_id = fields.Many2one(comodel_name="stock.lot", string="stock lot")
    product_template_id = fields.Many2one(comodel_name="product.template", string="product template")

