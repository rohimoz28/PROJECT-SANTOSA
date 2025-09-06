from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'sb.attendance.correction.details'
    _description = 'Attendance Correction Details'

    attn_correction_id = fields.Many2one(
        comodel_name='sb.attendance.corrections',
        string='Attendance Correction',
        required=False)
    period_id = fields.Many2one('hr.opening.closing', string='Periode', index=True)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True)
    nik = fields.Char(
        string='NIK',
        required=False)
    name = fields.Char(
        string='Name',
        required=False)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    division_id = fields.Many2one('sanhrms.division', string='Divisi', store=True, readonly="state =='done'")
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen', store=True, readonly="state =='done'")
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', store=True , readonly="state =='done'")
    job_id = fields.Many2one('hr.job', string='Job Position')
    wdcode = fields.Many2one(
        'hr.working.days',
        string='WD Code',
        copy=True,
        index=True
    )
    tgl_time_in = fields.Date(
        string='Tgl Time in',
        required=False)
    time_in = fields.Float(
        string='Time in',
        required=False)
    edited_time_in = fields.Float(
        string='Edited Time in',
        required=False)
    tgl_time_out = fields.Date(
        string='Tgl Time out',
        required=False)
    time_out = fields.Float(
        string='Time out',
        required=False)
    edited_time_out = fields.Float(
        string='Edited Time out',
        required=False)
    delay = fields.Float(
        string='Delay',
        required=False)
    remark = fields.Char(string='Remark', required=False)
    empgroup_id = fields.Many2one(comodel_name='hr.empgroup', string='Emp Group', required=False)
