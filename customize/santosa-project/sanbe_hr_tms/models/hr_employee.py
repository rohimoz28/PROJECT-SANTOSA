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
        'hr.employee', compute='get_parent_id', string="hr_employee parent id", store=True)
    emp_coach_id = fields.Many2one(
        'hr.employee', compute='get_coach_id', string="hr_employee coach id", store=True)
    # child_ids = fields.Many2many(
    #     'hr.employee', 'emp_parent_id', string="Bawahan")
    group_shift_id = fields.Many2one(
        'sb.mapping_employee.shift', string="Group Shift", store=True)

    @api.depends("parent_id")
    def get_parent_id(self):
        for line in self:
            if line.parent_id:
                line.emp_parent_id = self.env["hr.employee"].browse(
                    line.parent_id.id).id

    @api.depends("coach_id", "emp_parent_id")
    def get_coach_id(self):
        for line in self:
            parent_id = self.env["hr.employee"].browse(
                line.parent_id.id)
            if line.coach_id:
                line.emp_coach_id = self.env["hr.employee"].browse(
                    line.coach_id.id).id
            else:
                line.emp_coach_id = self.env["hr.employee"].browse(
                    parent_id.parent_id.id).id or parent_id.id
