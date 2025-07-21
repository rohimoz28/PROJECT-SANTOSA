# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EmpGroup(models.Model):
    _name = 'emp.group'
    _description = "Employee Group"
    

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active')
    responsible_id = fields.Many2one(
       'hr.employee',
       string='Penanggung Jawab')
    responsible_name = fields.Char(
       related= 'responsible_id.name', 
       Sstring='Penanggung Jawab', store=True)
    branch_id = fields.Many2one('res.branch', 
      string='Business Unit', 
      tracking=True, 
      default=lambda self: self.env.user.branch_id, required=True)
    employee_ids = fields.One2many(
       'hr.employee', 'employee_group1s', string='Karyawan')
    
    @api.depends('name', 'code','responsible_id')
    def _compute_display_name(self):
        for group in self:
              name = ''
              if group.code and group.name and group.responsible_id:
                name = '[' +  group.code +'] + ' + group.name + ' (' + group.responsible_id.name + ')'
              elif group.code and group.name and not group.responsible_id:
                name = '[' +  group.code +'] + ' + group.name
              group.display_name = name


class ServiceGroupsMST(models.Model):
    _name = 'mst.group.pelayanan'
    _description = "Master Group Pelayanan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    name = fields.Char('Name',required=True,tracking=True, index=True)
    code = fields.Char('Code',required=True,size=6,tracking=True, index=True)
    active = fields.Boolean('Active',default=True,tracking=True)
    sub_ids = fields.One2many('mst.sub.group.pelayanan','mst_id',string="Sub Unit")
    # branch_id = fields.Many2one('res.branch',string='Bisnis Unit',
    #   default=lambda self: self.env.user.branch_id,)
    _sql_constraints = [
        ('name_mst_pelayanan_uniq', 'unique(name)', 'The name must be unique!'),
        ('code_mst_pelayanan_uniq', 'unique(code)', 'The code must be unique!'),
    ]

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(ServiceGroupsMST, self).unlink()
      
    
class SubServiceGroupsMST(models.Model):
    _name = 'mst.sub.group.pelayanan'
    _description = "Sub Group Pelayanan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    name = fields.Char('Name', required=True, tracking=True, index=True)
    code = fields.Char('Code', required=True, size=6, tracking=True, index=True)
    active = fields.Boolean('Active',default=True,tracking=True)
    mst_id = fields.Many2one('mst.group.pelayanan', ondelete='cascade', index=True, copy=False)
    _sql_constraints = [
        ('name_sub_mst_pelayanan_uniq', 'unique(name)', 'The name must be unique!'),
        ('code_sub_mst_pelayanan_uniq', 'unique(code)', 'The code must be unique!'),
    ]
    
    
    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name :
              if not profesion.mst_id:
                name = '[' + profesion.code +'] ' + profesion.name
              else:
                name = '[' + profesion.mst_id.code + '-' + profesion.code +'] ' + profesion.name
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(SubServiceGroupsMST, self).unlink()
