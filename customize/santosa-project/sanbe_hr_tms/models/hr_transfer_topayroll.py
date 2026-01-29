# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict
from datetime import datetime
date_format = "%Y-%m-%d"


class HrTMSTransferToPayroll(models.TransientModel):
    _name = 'hr.transfer.payroll'
    _description = 'HR TMS Transfer To Payrool'

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search(
                    [('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search(
                [('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    def _get_active_periode_from(self):
        mycari = self.env['hr.opening.closing'].sudo().search(
            [('isopen', '=', True)], limit=1)
        return mycari.open_periode_from or False

    def _get_active_periode_to(self):
        mycari = self.env['hr.opening.closing'].sudo().search(
            [('isopen', '=', True)], limit=1)
        return mycari.open_periode_to or False

    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    branch_id = fields.Many2one(
        'res.branch', string='Business Unit', index=True, domain="[('id','in',branch_ids)]")
    department_id = fields.Many2one('hr.department', string='Sub Department')
    division_id = fields.Many2one(
        'sanhrms.division', string='Divisi', store=True)
    hrms_department_id = fields.Many2one(
        'sanhrms.department', string='Departemen', store=True)
    directorate_id = fields.Many2one(
        'sanhrms.directorate', string='Direktorat', store=True)
    job_id = fields.Many2one('hr.job', string='Job Position')

    periode_from = fields.Date(
        'Periode From', default=_get_active_periode_from)
    periode_to = fields.Date('Periode To', default=_get_active_periode_to)

    transfer_payroll_ids = fields.One2many(
        'hr.transfer.payroll_details', 'transfer_id', auto_join=True, string='Transfer To Payroll Details')

    def process_data(self):
        return


class HrTMSTransferToPayroll(models.TransientModel):
    _name = 'hr.transfer.payroll_details'
    _description = 'HR TMS Transfer To Payroll Details'

    transfer_id = fields.Many2one(
        'hr.transfer.payroll', string='Transfer To Payroll', index=True)
    nik = fields.Char('NIK')
    employee_id = fields.Many2one('hr.employee', string='Nama', index=True)
    department_id = fields.Many2one(
        'hr.department', string='Department', index=True)
    division_id = fields.Many2one(
        'sanhrms.division', related='employee_id.division_id', string='Divisi', store=True)
    hrms_department_id = fields.Many2one(
        'sanhrms.department', related='employee_id.hrms_department_id', string='Departemen', store=True)
    directorate_id = fields.Many2one(
        'sanhrms.directorate', related='employee_id.directorate_id', string='Direktorat', store=True)
    job_id = fields.Many2one(
        'hr.job', related='employee_id.job_id', string='Job Position')
    attendee_status = fields.Char('Attendee')
    pg_attendee = fields.Char('PG')
    aot1 = fields.Char('AOT1')
    aot2 = fields.Char('AOT2')
    aot3 = fields.Char('AOT3')
    aot4 = fields.Char('AOT4')
    apat = fields.Char('APAT')
    ansh = fields.Char('ANSH')
    status = fields.Char('Status')
    is_done = fields.Boolean(default=False)
