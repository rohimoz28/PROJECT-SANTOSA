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


class HRRecapitulation(models.Model):
    _name = "hr.tms.recap"
    _description = 'HR TMS Recapitulation'

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

    tms_from = fields.Date(string='TMS From')
    tms_to = fields.Date(string='To')
    tms_status = fields.Selection([('all','ALL')], string='Status')
    department_id = fields.Many2one('hr.department', string='Department')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee No')
    job_id = fields.Many2one('hr.job', string='Job Title')
    recap_ids = fields.One2many('hr.tms.recapdetails', 'recap_id', auto_join=True, string='Recapitulation Details')

    area_id = fields.Many2one('res.territory', string='Area ID')
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True, domain="[('id','in',branch_ids)]")

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
class HRRecapitulationDetails(models.Model):
    _name = "hr.tms.recapdetails"
    _description = 'HR TMS Recapitulation Details '

    recap_id = fields.Many2one('hr.tms.recap', string='Recapitulation ID')
    employee_name = fields.Char('Employee Name', related='recap_id.employee_id.name')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    wo_code = fields.Char(string='WO Code')
    attendee = fields.Integer(string='Attendeee')
    sick = fields.Integer(string='Sick')
    absent = fields.Integer(string='Absent')
    leaves = fields.Integer(string='Leave')
    permission = fields.Integer(string='Permission')
    ot1 = fields.Char(string='OT1')
    ot2 = fields.Char(string='OT2')
    ot3 = fields.Char(string='OT3')

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