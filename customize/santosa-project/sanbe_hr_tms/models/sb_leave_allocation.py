from odoo import fields, models, api
import logging
from datetime import datetime


class SbLeaveAllocation(models.Model):
    _name = 'sb.leave.allocation'
    _description = 'Table For Populating Employee Leave Allocation'

    leave_allocation = fields.Float(string='Leave Adjustment', required=False, default=0)
    leave_remaining= fields.Float(string='Remaining Leave', store=True)
    leave_used= fields.Float(string='Leave Used', required=False, default=0)
    area_id = fields.Many2one('res.territory', string='Area', index=True, required=True)
    branch_id = fields.Many2one('res.branch',string='Business Unit', tracking=True, required=True)
    department_id = fields.Many2one('hr.department', string='Sub Department', index=True, required=True)
    division_id = fields.Many2one('sanhrms.division', string='Divisi', store=True,)
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen', store=True,)
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', store=True , )
    job_id = fields.Many2one('hr.job', string='Job Position', index=True, required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', index=True, tracking=True, required=True)
    date = fields.Date(string='Date', tracking=True, default=datetime.today(), required=True)
    remarks = fields.Char(string='Remarks', tracking=True)
    description = fields.Text(string='Description', tracking=True)

    @api.onchange('employee_id',)
    def get_employee_data(self):
        for rec in self:
            if rec.employee_id:
                rec.area_id = rec.employee_id.area
                rec.branch_id = rec.employee_id.branch_id
                rec.department_id = rec.employee_id.department_id
                rec.job_id = rec.employee_id.job_id
            else:
                rec.area_id = False
                rec.branch_id = False
                rec.department_id = False
                rec.job_id = False

    @api.onchange('employee_id', 'leave_allocation', 'leave_used')
    def _compute_leave_remaining(self):
        for rec in self:
            if rec.employee_id:
                last_leave = self.env['sb.leave.allocation'].search([
                    ('employee_id', '=', rec.employee_id.id)
                ], order='id desc', limit=1)

                if last_leave:
                    rec.leave_remaining = last_leave.leave_remaining

                    if rec.leave_allocation > 0:
                        rec.leave_used = 0
                        rec.leave_remaining = last_leave.leave_remaining + rec.leave_allocation
                    if rec.leave_used > 0:
                        rec.leave_allocation = 0
                        rec.leave_remaining = last_leave.leave_remaining - rec.leave_used

                else:
                    if rec.leave_allocation > 0:
                        rec.leave_used = 0
                        rec.leave_remaining = rec.leave_allocation
                    else:
                        rec.leave_remaining = 0

                    if rec.leave_used > 0:
                        rec.leave_allocation = 0
                        rec.leave_remaining = rec.leave_remaining - rec.leave_used

                if rec.leave_remaining < 0:
                    rec.leave_remaining = 0
                elif rec.leave_remaining > 16:
                    rec.leave_remaining = 16


    def _cron_populate_leave_alloc(self):
        _logger = logging.getLogger(__name__)
        try:
            self.env.cr.execute("CALL procedure_leave_alloc()")
            self.env.cr.commit()
            _logger.info("Cron For Populate Leave Allocation is Running Successfully.")
        except Exception as e:
            self.env.cr.rollback()
            _logger.error("Error running Cron for Populate Leave Allocation: %s", str(e))


    def unlink(self):
        return super(SbLeaveAllocation, self).unlink()