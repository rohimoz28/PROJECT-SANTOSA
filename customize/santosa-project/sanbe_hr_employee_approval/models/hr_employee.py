# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    state = fields.Selection([
        ('draft', "Draft"),
        ('req_approval', 'Request For Approval'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('inactive', 'Inactive'),
        ('hold', 'Hold'),
    ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,store=True,
        default='draft')

    hold_allowed_user = fields.Boolean(
        compute='_compute_hold_allowed_user',
        store=False
    )

    def _compute_hold_allowed_user(self):
        for rec in self:
            user = self.env.user
            rec.hold_allowed_user = user.login == 'gurnita' or user.has_group('base.group_system')

    def request_for_approval(self):
        return self.write({'state': 'req_approval'})

    def action_reject(self):
        return self.write({'state': 'rejected'})

    def action_hold(self):
        return self.write({'state': 'hold'})

    def action_set_approved(self):
        return self.write({'state': 'approved'})

    def action_approval(self):
        self.ensure_one()
        for data in self.env['hr.employee'].browse(self.ids):
            if data.nik:
                data_upload_attendance = self.env['data.upload.attendance'].sudo().search([
                    ('nik', '=', self.nik)
                ])

                if data_upload_attendance:
                    data_employee = {
                        'employee_id': data.id,
                        'nik': data.nik,
                        'area_id': data.area.id,
                        'branch_id': data.branch_id.id,
                        'state': 'register'
                    }
                    data_upload_attendance.write(data_employee)
        datalog = {'employee_id': self.id,
                   'service_type': 'NEWS',
                   'start_date': self.join_date,
                   'end_date': False,
                   'bisnis_unit': self.branch_id.id,
                   'department_id': self.department_id.id,
                   'job_title': self.job_id.name,
                   'job_status': self.job_status,
                   'emp_status': self.emp_status}
        self.env['hr.employment.log'].sudo().create(datalog)
        return self.write({'state': 'approved'})

    def unlink(self):
        for record in self:
            adatrans = False
            mytrans = self.env['hr.employee.mutations'].sudo().search([('employee_id', '=', record.id)])
            if mytrans:
                adatrans = True
            myresig = self.env['hr.resignation'].sudo().search([('employee_id', '=', record.id)])
            if myresig:
                adatrans = True
            if record.state == 'draft':
                return super().unlink()
            else:
                if adatrans == True:
                    raise UserError('It cannot be deleted because there is already a transaction')
                else:
                    return super().unlink()
