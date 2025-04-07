# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrProfesionMedic(models.Model):
    _name = 'hr.profesion'
    _description = 'Hr Profesion Medical'

    type = fields.Selection([('medic','Medis'),('nurse','Perawat'),('other','Kategory Khusus')],'Type')
    name = fields.Char('Name')
    code = fields.Char('Code', required=True, size=20, unique=True)


    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] + ' + profesion.name
            profesion.display_name = name