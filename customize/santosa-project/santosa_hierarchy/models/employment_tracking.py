from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)
ORDER_STATE = [
    ('draft', "Draft"),
    ('approved', "Approved"),
]


class HrEmployementTracking(models.TransientModel):
    _name = 'hr.employment.tracking'
    _description = 'HR Employement Tracking'

    idpeg = fields.Char('id pegawai')
    emp_no = fields.Many2one('hr.employee', string='Employee No', index=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee ID', index=True)
    employee_name = fields.Char(string='Employee Name')
    nik = fields.Char('NIK')
    area = fields.Char('Area')
    bisnis_unit = fields.Char('Business Unit')
    departmentid = fields.Char('Sub Department')
    state = fields.Selection(
        selection=ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    jobstatus = fields.Char('Job Status')
    employementstatus = fields.Char('Employeement Status')
    jobtitle = fields.Char('Job Position')
    empgroup = fields.Char('Employee P Group')

    tracking_ids = fields.One2many('hr.employment.trackingdetails', 'tracking_id',
                                   string='Employment Details', auto_join=True, index=True)

    def button_approve(self):
        return self.write()

    def pencarian_data(self):
        return

    @api.onchange('emp_no')
    def _isi_data_employee(self):
        for alldata in self:
            if not alldata.emp_no:
                return
            alldata.tracking_ids = [Command.set([])]
            myemp = alldata.emp_no
            alldata.nik = myemp.nik
            alldata.employee_id = myemp.id
            alldata.employee_name = myemp.name
            alldata.area = myemp.area.name
            alldata.bisnis_unit = myemp.department_id.branch_id.name
            alldata.departmentid = myemp.department_id.name
            alldata.jobstatus = myemp.job_status
            alldata.employee_group1s = myemp.employee_group1s.name
            alldata.doc_number = myemp.name
            alldata.end_contract = myemp.end_contract
            alldata.area = myemp.area.id
            alldata.directorate_id = myemp.directorate_id.id
            alldata.hrms_department_id = myemp.hrms_department_id.id
            alldata.division_id = myemp.division_id.id
            alldata.parent_id = myemp.employee_id.parent_id.id
            empstat = ''
            if myemp.emp_status:
                empstat = myemp.emp_status
            else:
                empstat = myemp.emp_status
            alldata.employementstatus = empstat
            alldata.jobtitle = myemp.job_id.name
            empgroup = myemp.employee_group1
            alldata.empgroup = empgroup
            mycari = self.env['hr.employment.log'].sudo().search(
                [('employee_id', '=', int(myemp.id))])
            mydetails = self.env['hr.employment.trackingdetails']
            myempstat = ''
            if mycari:
                cnt = 0
                for allcari in mycari:
                    if cnt == 0:
                        myempstat = allcari.emp_status
                    mydetails |= self.env['hr.employment.trackingdetails'].sudo().create({
                        'service_type': allcari.service_type,
                        'start_date': allcari.start_date,
                        'end_date': allcari.end_date,
                        'bisnis_unit': allcari.bisnis_unit.id,
                        'department_id': allcari.department_id.id,
                        'job_title': allcari.job_title,
                        'job_status': allcari.job_status,
                        'emp_status': allcari.emp_status,
                        'employee_group1s': allcari.employee_group1s.name,
                        'doc_number': allcari.name,
                        'end_contract': allcari.end_contract,
                        'area': allcari.area.id,
                        'directorate_id': allcari.directorate_id.id,
                        'hrms_department_id': allcari.hrms_department_id.id,
                        'division_id': allcari.division_id.id,
                        'parent_id': allcari.employee_id.parent_id.id, })
                    cnt += 1

            alldata.employementstatus = myempstat
            alldata.tracking_ids = mydetails.ids

    def isi_details_tracking(self, dataid):
        data = self.sudo()
        if data.tracking_ids:
            data.tracking_ids.unlink()
        mycari = self.env['hr.employment.log'].sudo().search(
            [('employee_id', '=', int(dataid))])
        mydetails = self.env['hr.employment.trackingdetails']
        if mycari:
            for allcari in mycari:
                mydetails |= self.env['hr.employment.trackingdetails'].sudo().create({
                    'service_type': allcari.service_type,
                    'start_date': allcari.start_date,
                    'end_date': allcari.end_date,
                    'bisnis_unit': allcari.bisnis_unit.id,
                    'department_id': allcari.department_id.id,
                    'job_title': allcari.job_title,
                    'job_status': allcari.job_status,
                    'emp_status': allcari.emp_status})

        data.tracking_ids = mydetails.ids

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view


class HrEmployementTrackingDetails(models.TransientModel):
    _name = 'hr.employment.trackingdetails'
    _description = 'HR Employement Tracking Details'

    tracking_id = fields.Many2one(
        'hr.employment.tracking', string='Tracking ID', index=True)
    service_type = fields.Char('Service Type')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End date')
    bisnis_unit = fields.Many2one('res.branch', string='BU')
    department_id = fields.Many2one('hr.department', string='Dept')
    sub_dept = fields.Many2one('hr.department', string='Sub Dept')
    job_title = fields.Char('Job Title')
    job_status = fields.Selection([('permanent', 'Permanent'),
                                   ('contract', 'Contract'),
                                   ('outsource', 'Out Source')], default='contract', string='Job Status')
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired')], default='probation', string='Employement Status')

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view
