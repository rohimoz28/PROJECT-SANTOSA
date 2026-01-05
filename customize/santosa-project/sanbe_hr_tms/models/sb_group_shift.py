# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SbGroupShift(models.Model):
    _name = 'sb.group.shift'
    _description = 'Master Group Shift'
    _order = 'active desc, code asc'

    code = fields.Char('Code',
                       index=True, required=True,
                       size=5, help=" Code for master group shifting",)
    name = fields.Char('Description',
                       index=True, required=True,
                       default="New", help=" Description for master group shifting",)
    active = fields.Boolean(
        string='Active', default=True
    )

    _sql_constraints = [
        # (
        #     'unique_name',
        #     'UNIQUE(name)',
        #     'Another entry with the same name already exists.'
        # ),
        (
            'unique_code',
            'UNIQUE(code)',
            'Another entry with the same code already exists.'
        ),
    ]
