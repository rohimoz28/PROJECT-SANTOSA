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
