import pdb

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import pytz
from datetime import date, datetime, time, timedelta

class StgTransformAbsent (models.Model):
    _name = "stg.transform.absent"
    _description = 'Staging Transform Absent'

    # emp_firstname = fields.Char('Employee')
    # emp_code = fields.Char('NIK')
    # dept_code = fields.Char('Department Code')
    # emp_type = fields.Char('Employee Type')
    # emp_group = fields.Char('Employee Group')
    # userid = fields.Char('User ID')
    # dept_name = fields.Char('Department')
    # date = fields.Date('Date')
    # time = fields.Float('Time')
    # in_out = fields.Char('In Out')

    userid = fields.Char('Badges Number')
    logtime = fields.Datetime('Log time')
    terminal = fields.Char('Terminal')
    status = fields.Char('Status')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    