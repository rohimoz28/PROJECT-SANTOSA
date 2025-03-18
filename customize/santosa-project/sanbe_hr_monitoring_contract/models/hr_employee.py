# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    end_date = fields.Date('End Date',related='contract_id.date_end')
    contract_id = fields.Many2one('hr.contract')

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    @api.onchange('state')
    def update_employee_contract(self):
        for line in self:
            for contracts in self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1,order='date_end desc'):
                self.employee_id.contract_id = contracts.id