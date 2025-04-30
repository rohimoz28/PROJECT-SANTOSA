# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrProfesion(models.Model):
    _name = 'hr.profesion'
    _description = 'Hr Profesion Medical'

    type = fields.Selection([('medic','Medis'),('nurse','Perawat'),('other','Keahlian Khusus')],'Type')
    name = fields.Char('Name')
    descr = fields.Char('Description')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char('Code', required=True, size=20, unique=True)


    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name
            
class HrProfesionMedic(models.Model):
    _name = 'hr.profesion.medic'
    _description = 'Hr Profesion Medical'

    name = fields.Char('Name')
    descr = fields.Char('Description')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char('Code', required=True, size=20, unique=True)


    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(HrProfesionMedic, self).unlink()

            
class HrProfesionNurse(models.Model):
    _name = 'hr.profesion.nurse'
    _description = 'Hr Profesion Medical'

    name = fields.Char('Name')
    descr = fields.Char('Description')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char('Code', required=True, size=20, unique=True)


    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name
            
    # @api.model
    def unlink(self):
        return super(HrProfesionNurse, self).unlink()
            
class HrProfesionSpecial(models.Model):
    _name = 'hr.profesion.special'
    _description = 'Hr Profesion non Medical'

    name = fields.Char('Name')
    descr = fields.Char('Description')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis', tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char('Code', required=True, size=20, unique=True)


    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name
            
    # @api.model
    def unlink(self):
        return super(HrProfesionSpecial, self).unlink()
    
class HrWorkUnit(models.Model):
    _name = 'hr.work.unit'
    _description = 'Unit Kerja'

    name = fields.Char('Name')
    descr = fields.Char('Description')
    area = fields.Many2one('res.territory', string='Area', tracking=True, required=True)
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis', tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char('Code', required=True, size=20, unique=True)


    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(HrWorkUnit, self).unlink()