# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    badges_nos = fields.Many2many(
        'hr.machine.details', 'name', 'employee_id', string='Badges Number')
    workingdays_id = fields.Many2one(
        'hr.working.days', domain="['|',('available_for','in',branch_id),('available_for','=',False)]")
    emp_parent_id = fields.Many2one(
        'hr.employee', compute="get_emp_parent_id", store=True, readonly=False)
    child_ids = fields.One2many(
        'hr.employee', 'emp_parent_id', string='Direct subordinates')

    @api.depends('parent_id')
    def get_emp_parent_id(self):
        for line in self:
            if line.parent_id:
                line.emp_parent_id = self.env['hr.employee'].browse(
                    line.parent_id.id).id