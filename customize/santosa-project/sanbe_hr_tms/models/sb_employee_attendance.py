from odoo import fields, models, api


class SbEmployeeAttendance(models.Model):
    _name = 'sb.employee.attendance'
    _description = 'For Monitoring Employee Attendance'

    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    area_id = fields.Many2one('res.territory', string='Area ID', index=True, readonly="state =='done'")
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True, readonly="state =='done'")
    department_id = fields.Many2one('hr.department', string='Sub Department', readonly="state =='done'")
    division_id = fields.Many2one('sanhrms.division', string='Divisi', store=True, readonly="state =='done'")
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen', store=True, readonly="state =='done'")
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', store=True , readonly="state =='done'")
    nik = fields.Char(
        string='NIK',
        required=False)
    details_date = fields.Date(
        string='Date',
        required=False)
    empgroup_id = fields.Many2one(
        comodel_name='hr.empgroup',
        string='Employee Group',
        required=False
    )
    time_in = fields.Float(
        string='Time In',
        required=False)
    time_out = fields.Float(
        string='Time Out',
        required=False)
    status_attendance = fields.Char(
        string='Status Attendance',
        required=False)
    periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True)
