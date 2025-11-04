from odoo import fields, models, api,  _, Command
from odoo.exceptions import ValidationError, UserError
import logging

class SbRouteMaster(models.Model):
    _name = 'sb.route.master'

    name = fields.Char('Name', compute='_compute_name_route', store=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit')
    route_code = fields.Char('Route Code')
    route_description = fields.Char('Route Description')
    is_active = fields.Boolean('Active', default=True)
    employee_ot_ids = fields.One2many('hr.overtime.employees', 'route_id', string='Overtime Employees')


    @api.constrains('route_code','route_description')
    def duplicate_route_check(self):
        for rec in self:
            duplicate_code = self.search([
                ('id', '!=', rec.id),
                ('route_code','=',rec.route_code),
            ])
            if duplicate_code:
                raise ValidationError(f"Duplicate route code found: {rec.route_code}.")
    
    @api.depends('route_code')
    def _compute_name_route(self):
        for rec in self:
            if rec.route_code:
                rec.name = f'{rec.route_code} - {rec.route_description}'
            