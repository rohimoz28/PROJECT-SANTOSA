# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)
ORDER_STATE = [
    ('draft', "Draft"),
    ('approved', "Approved"),
]


class HrEmployementlog(models.Model):
    _name = 'hr.employment.log'
    _description = 'HR Employement Log'
    _order = 'create_date desc, id desc'

    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    contract_id = fields.Many2one(related="employee_id.contract_id", string="Contract", store=True)
    service_type = fields.Char('Service Type', tracking=True)
    start_date = fields.Date('Start Date', tracking=True)
    end_date = fields.Date('End date', tracking=True)
    area = fields.Many2one('res.territory', string='Area', tracking=True)
    bisnis_unit = fields.Many2one('res.branch', string='Business Units', tracking=True)
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', tracking=True)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen', tracking=True)
    division_id = fields.Many2one('sanhrms.division', string='Divisi', tracking=True)
    job_title = fields.Char(string='Jabatan', tracking=True)
    parent_id = fields.Many2one('parent.hr.employee', tracking=True, string='Atasan Langsung')
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], default='contract', tracking=True, string='Status Hubungan Kerja')
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('transfer_to_group', 'Transfer To Group'),
                                   ('terminated', 'Terminated'),
                                   ('pass_away', 'Pass Away'),
                                   ('long_illness', 'Long Illness')], default='probation', string='Status Kekaryawanan')
    emp_status_id = fields.Many2one(comodel_name='hr.emp.status', string='Status Kekaryawanan', tracking=True)
    masa_jabatan = fields.Char('Masa Jabatan', compute='hitung_masa_jabatan', store=False)
    nik = fields.Char('NIK', compute='_get_nik', store=True)
    employee_group1 = fields.Char(string="Group Penggajian", compute='_get_nik')
    model_name = fields.Char(string="Model Name")
    model_id = fields.Integer(string="Model Id")
    trx_number = fields.Char(string="Nomor Transaksi")
    doc_number = fields.Char(string="Nomor Dokumen")
    # end_contract = fields.Boolean(string="Flag End of Contract", default=False)
    end_contract = fields.Boolean(string="Rehire", default=False)
    label = fields.Char(default="Open View")
    employee_group1s = fields.Char(string='Group penggajian', compute='_get_nik' , tracking=True, store=True)
    

    def ambil_view(self):
        for rec in self:
            if rec.model_name and rec.model_id:
                return {
                    'type': 'ir.actions.act_window',
                    'name': rec.model_name,
                    'view_mode': 'form',
                    'res_model': rec.model_name,
                    'res_id': rec.model_id,
                    'target': 'current',
                    'context': {'create': False, 'delete': False, 'edit': False},
                }

    @api.depends('employee_id')
    def _get_nik(self):
        for rec in self:
            if rec.employee_id:
                rec.nik = rec.employee_id.nik
                rec.employee_group1s = rec.employee_id.employee_group1s.name

    # @api.depends('start_date', 'end_date')
    # def hitung_masa_jabatan(self):
    #     for record in self:
    #         service_util = False
    #         myear = 0
    #         mmonth = 0
    #         mday = 0
    #         if record.employee_id.job_status == 'contract':
    #             mycont = self.env['hr.contract'].sudo().search(
    #                 [('employee_id', '=', record.employee_id.id), ('date_end', '<=', record.start_date)], limit=1)
    #             if mycont:
    #                 service_until = mycont.date_end
    #                 if mycont.date_start and service_until > mycont.date_start:
    #                     service_duration = relativedelta(
    #                         service_until, mycont.date_start
    #                     )
    #                     myear = service_duration.years
    #                     mmonth = service_duration.months
    #                     mday = service_duration.days
    #         else:
    #             if record.start_date and record.end_date:
    #                 service_until = record.end_date
    #             else:
    #                 service_until = fields.Date.today()
    #             if record.start_date and service_until > record.start_date:
    #                 service_duration = relativedelta(
    #                     service_until, record.start_date
    #                 )
    #                 myear = service_duration.years
    #                 mmonth = service_duration.months
    #                 mday = service_duration.days
    #         masajab = 'Year %s Month %s Days %s' % (myear, mmonth, mday)
    #         record.masa_jabatan = masajab

    @api.depends('start_date', 'end_date')
    def hitung_masa_jabatan(self):
        for record in self:
            myear = 0
            mmonth = 0
            mday = 0
            if record.start_date and record.end_date:
                service_duration = relativedelta(record.end_date, record.start_date)
                myear = service_duration.years
                mmonth = service_duration.months
                mday = service_duration.days
            masajab = 'Year %s Month %s Days %s' % (myear, mmonth, mday)
            record.masa_jabatan = masajab

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view
