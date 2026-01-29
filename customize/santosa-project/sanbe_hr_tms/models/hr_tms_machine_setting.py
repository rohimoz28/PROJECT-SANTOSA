# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError
from odoo.osv import expression
import pytz
from datetime import datetime


class HRTmsMachineSetting(models.Model):
    _name = "hr.machine.setting"
    _description = 'HR TMS MAchine Setting'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    # Function For Filter Branch in Area
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    name = fields.Char(string='Name', index=True)
    id_fingerprint = fields.Char(string='ID Fingerprint')
    ip_fingerprint = fields.Char(string='IP Fingerprint')
    port_fingerprint = fields.Char(string='Port Fingerprint')

    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Units', index=True, domain="[('id','in',branch_ids)]")

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

class HRTmsMachineDetails(models.Model):
    _name = "hr.machine.details"
    _description = 'HR TMS Machine Details Setting'
    _rec_name = 'name'

    name = fields.Char('Badges Number')
    employee_id = fields.Many2one('hr.employee',string='Employee Name',index=True)
    nik = fields.Char('NIK', compute='_compute_nik', store=True)
    job_id = fields.Many2one('hr.job',string='Job Position',compute='_compute_job_id',store=True,index=True)
    department_id = fields.Many2one('hr.department',string='Sub Department',compute='_compute_department_id',store=True,index=True)

    division_id = fields.Many2one(
        comodel_name='sanhrms.division',
        string='Division',
        related='employee_id.division_id',
        required=False,
        ondelete='restrict')

    hrms_department_id = fields.Many2one(
        comodel_name='sanhrms.department',
        string='Department',
        related='employee_id.hrms_department_id',
        required=False,
        ondelete='restrict')

    directorate_id = fields.Many2one(
        comodel_name='sanhrms.directorate',
        string='Directorate',
        related='employee_id.directorate_id',
        required=False,
        ondelete='restrict')
    branch_id = fields.Many2one('res.branch',string='Branch',compute='_compute_branch_id',store=True,index=True)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._context.get('employee_nik'):
                myemp = self.env['hr.employee'].sudo().search([('nik','=',self._context.get('employee_nik'))],limit=1)
                vals['employee_id'] = myemp.id
        employees = super().create(vals_list)
        return employees

    @api.depends('employee_id.nik')
    def _compute_nik(self):
        for record in self:
            record.nik = record.employee_id.nik
    
    @api.depends('employee_id.job_id')
    def _compute_job_id(self):
        for record in self:
            record.job_id = record.employee_id.job_id
    
    @api.depends('employee_id.department_id')
    def _compute_department_id(self):
        for record in self:
            record.department_id = record.employee_id.department_id

    @api.depends('employee_id.branch_id')
    def _compute_branch_id(self):
        for record in self:
            record.branch_id = record.employee_id.branch_id