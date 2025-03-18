# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import pytz
from datetime import timedelta, datetime, time,date


class CalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    #Function FOr Filtter Branch Based On Area ID
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    area_id = fields.Many2one("res.territory", string='Area ID',index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Bisnis Unit', index=True, domain="[('id','in',branch_ids)]")
    color = fields.Integer("Color")
    state = fields.Selection(selection=[('draft','Draft'),('post','Posted')], default='draft')

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
        
    def action_posted(self):
        for rec in self:
            dt1 = ((datetime.strptime(str(rec.date_from), "%Y-%m-%d %H:%M:%S"))+timedelta(hours=7)).date()
            dt2 = (((datetime.strptime(str(rec.date_to), "%Y-%m-%d %H:%M:%S")))+timedelta(hours=7)).date()
            
            if rec.area_id and rec.branch_id:
                dt_entry = self.env['hr.attendance'].sudo().search([('dates','>=',dt1),('dates','<=',dt2),('area_id','=',rec.area_id.id),('branch_id','=',rec.branch_id.id)])
            elif rec.area_id and not(rec.branch_id):
                dt_entry = self.env['hr.attendance'].sudo().search([('dates','>=',dt1),('dates','<=',dt2),('area_id','=',rec.area_id.id)])
            elif not(rec.area_id) and rec.branch_id:
                dt_entry = self.env['hr.attendance'].sudo().search([('dates','>=',dt1),('dates','<=',dt2),('branch_id','=',rec.branch_id.id)])
            elif not(rec.area_id) and not(rec.branch_id):
                dt_entry = self.env['hr.attendance'].sudo().search([('dates','>=',dt1),('dates','<=',dt2)])
            if dt_entry:
                for rex in dt_entry:
                    rex.write({'day_type':'h'})
            rec.state = 'post'
    
    @api.model
    def get_unusual_days(self, date_from, date_to=None):
        employee_id = self.env.context.get('employee_id', False)
        employee = self.env['hr.employee'].browse(employee_id) if employee_id else self.env.user.employee_id
        return employee.sudo(False)._get_unusual_days(date_from, date_to)

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name','in',['User TMS','HRD CA'])])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
                for node in arch.xpath("//tree"):
                    node.set('create', '0')
                for node in arch.xpath("//form"):
                    node.set('create', '0')
        return arch, view
class CalendarLeaves(models.Model):
    _inherit = "hr.leave.type"

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name','in',['User TMS','HRD CA'])])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
                for node in arch.xpath("//tree"):
                    node.set('create', '0')
                for node in arch.xpath("//form"):
                    node.set('create', '0')
                for node in arch.xpath("//form[@string='Save & Close']"):
                    node.set('invisible', 'True')
        return arch, view