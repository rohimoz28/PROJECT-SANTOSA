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

import datetime

def addYears(date, years):
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


    periode_probation = fields.Integer('Periode Probation',readonly="job_status != 'permanent'")
    ext_probation = fields.Integer('Ext Prob',readonly="job_status != 'permanent'")
    confirm_probation = fields.Date('Confirmation Date')
    retire_age = fields.Integer('Retire Age')
    pension_date = fields.Date('Pension Date',)
    bond_service = fields.Boolean('Bond Services',default=False)
    service_from = fields.Date('Service From')
    service_to = fields.Date('To')
    is_pinalty = fields.Boolean('Pinalty',default=False)
    pinalty_bs = fields.Integer('Pinalty BS')

    pinalty_amount = fields.Monetary('Penalty Amount')
    resign_notice = fields.Integer('Resign Notice')
    asset_ids = fields.One2many('hr.employee.assets','employee_id',auto_join=True,string='Asset Details')
    is_prob = fields.Boolean(default=False, string='Is Prob', compute='_isi_confirm_probation')

    @api.onchange('periode_probation','ext_probation')
    @api.depend('periode_probation','ext_probation')
    def _isi_confirm_probation(self):
        for rec in self:
            if rec.periode_probation == 0 and rec.ext_probation == 0:
                rec.is_prob = True
                if rec.joining_date:
                    rec.confirm_probation = rec.join_date

    @api.model
    def create(self, vals):
        res = super(HREmployee, self).create(vals)
        for rec in self:
            if rec.job_status == 'contract':
                rec.retire_age = 0
                rec.periode_probation = 0
                rec.joining_date = False
        return res
    
    def write(self,vals_list):
        res = super(HREmployee,self).write(vals_list)
        for rec in self:
            if rec.job_status == 'contract':
                rec.retire_age = 0
                rec.periode_probation = 0
                rec.joining_date = False
        return res
        
    @api.onchange('retire_age')
    def _isi_pensiun(self):
        for alldatarec in self:
            if not alldatarec.retire_age or alldatarec.retire_age==0:
                alldatarec.pension_date = False
                return
            usiapensiun = alldatarec.retire_age
            haruspensiun = addYears(alldatarec.birthday,int(usiapensiun))
            alldatarec.pension_date = haruspensiun


class HREmployeeAssets(models.Model):
    _name = "hr.employee.assets"

    employee_id = fields.Many2one('hr.employee',string='Employee ID',index=True)
    asset_name = fields.Char('Asset/Benefit Type')
    asset_number = fields.Char('Asset/Benefit Number')
    uom = fields.Many2one('uom.uom',string='UOM')
    asset_qty = fields.Float('QTY')
    keterangan = fields.Text('Keterangan')

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
               group_name = self.env['res.groups'].search([('name','=','HRD CA')])
               cekgroup = self.env.user.id in group_name.users.ids
               if cekgroup:
                   for node in arch.xpath("//field"):
                          node.set('readonly', 'True')
                   for node in arch.xpath("//button"):
                          node.set('invisible', 'True')
        return arch, view