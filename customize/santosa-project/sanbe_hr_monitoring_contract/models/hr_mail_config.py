# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrMailConfig(models.Model):
    _name = 'hr.mail.config'
    _description = 'Config Receiver Notification Contract Employee'
    _inherit =['mail.thread']

    name = fields.Char('Name', 
    default='New',related='branch_id.name'
    )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.company_id.id)
    branch_id = fields.Many2one('res.branch', string='Business Unit', required=True)
    list_email = fields.Text('Recive Mail', required=True, default='')
    day7 = fields.Boolean('7 days')
    day14 = fields.Boolean('day 14')
    day30 = fields.Boolean('day 30')
    day60 = fields.Boolean('day 60')
    active = fields.Boolean(
    default=True
    )
    _sql_constraints = [
        ('name_monitoring_uniq', 'unique (branch_id,company_id)', "Receiver Per Business Unit")
    ]

