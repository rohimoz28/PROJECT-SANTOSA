# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WizActContractMonitoring(models.TransientModel):
    _name = 'wiz.act.contract.monitoring'
    _description = _('WizActContractMonitoring')

    name = fields.Char(_('Name'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_name = fields.Char('Employee Name', related = 'employee_id.name', required=True)
    nik_employee = fields.Char('Employee NIK', related = 'employee_id.nik', required=True)
    superior_id = fields.Many2one('hr.employee','Immediate Superior', related = 'employee_id.parent_id', required=True)
    company_id = fields.Many2one('res.company',related='employee_id.company_id', string='Company', required=True)
    branch_id = fields.Many2one('res.branch', related='employee_id.branch_id', string='Branch', required=True)
    territory_id = fields.Many2one('res.territory', related='employee_id.area', string='Area', required=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', tring='Department', required=True)
    job_id = fields.Many2one('hr.job', string='Job', related='employee_id.job_id', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True)
    
    def new_contract(self):
        _logger.info('Hello Wizard')

    def exit_employee(self):
        _logger.info('Hello Wizard')
