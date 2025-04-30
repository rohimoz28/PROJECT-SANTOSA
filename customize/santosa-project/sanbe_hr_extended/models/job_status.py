# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class JobStatus(models.Model):
    _name = 'sanhrms.job.status'
    _description = 'Job Status'

    name = fields.Char('Name', required=True, index=True)
    type = fields.Selection([('pkwt', 'PKWT'),
                                   ('pkwtt', 'PKWTT'),
                                   ('outsource', 'Outsource'),
                                   ('internship', 'Magang'),
                                   ('mitra', 'Mitra'),
                                   ('visitor', 'Visitor'),
                                   ('tka', 'TKA'),
                                   ], string='Type',required=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', tracking=True, default=lambda self: self.env.user.branch_id, required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char('Code', required=True, size=20, unique=True)

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name + '(' + profesion.type.upper() + ')'
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(JobStatus, self).unlink()


