# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

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
    emp_no = fields.Many2one('hr.employee',string='Employee No',index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
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

    tracking_ids = fields.One2many('hr.employment.trackingdetails','tracking_id',string='Employment Details',auto_join=True,index=True)

    def unlink(self):
        return super(HrEmployementTracking, self).unlink()

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
            empstat = ''
            if myemp.emp_status:
                empstat = myemp.emp_status
            else:
                empstat = myemp.emp_status
            alldata.employementstatus = empstat
            alldata.jobtitle = myemp.job_id.name
            empgroup =myemp.employee_group1
            alldata.empgroup = empgroup
            mycari = self.env['hr.employment.log'].sudo().search([('employee_id', '=', int(myemp.id))])
            mydetails = self.env['hr.employment.trackingdetails']
            myempstat = ''
            if mycari:
                cnt =0
                for allcari in mycari:
                    if cnt == 0:
                        myempstat =  allcari.emp_status
                    mydetails |= self.env['hr.employment.trackingdetails'].sudo().create({
                        'service_type': allcari.service_type,
                        'start_date': allcari.start_date,
                        'end_date': allcari.end_date,
                        'bisnis_unit': allcari.bisnis_unit.id,
                        'department_id': allcari.department_id.id,
                        'job_title': allcari.job_title,
                        'job_status': allcari.job_status,
                        'emp_status': allcari.emp_status})
                    cnt += 1

            alldata.employementstatus = myempstat
            alldata.tracking_ids = mydetails.ids


    def isi_details_tracking(self,dataid):
            data = self.sudo()
            if data.tracking_ids:
                data.tracking_ids.unlink()
            mycari = self.env['hr.employment.log'].sudo().search([('employee_id','=',int(dataid))])
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
               group_name = self.env['res.groups'].search([('name','=','HRD CA')])
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

    tracking_id = fields.Many2one('hr.employment.tracking',string='Tracking ID', index=True)
    service_type = fields.Char('Service Type')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End date')
    bisnis_unit = fields.Many2one('res.branch',string='BU')
    department_id = fields.Many2one('hr.department',string='Dept')
    sub_dept = fields.Many2one('hr.department',string='Sub Dept')
    job_title = fields.Char('Job Title')
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], default='contract', tracking=True, string='Status Hubungan Kerja')
    emp_status = fields.Selection([('probation','Probation'),
                                   ('confirmed','Confirmed'),
                                   ('resigned','Resigned'),
                                   ('retired','Retired')],default='probation',string='Employement Status')

    def unlink(self):
        return super(HrEmployementTrackingDetails, self).unlink()

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
               group_name = self.env['res.groups'].search([('name','=','HRD CA')])
               cekgroup = self.env.user.id in group_name.users.ids
               if cekgroup:
                   for node in arch.xpath("//field"):
                          node.set('readonly', 'True')
                   for node in arch.xpath("//button"):
                          node.set('invisible', 'True')
        return arch, view
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    @api.model
    def get_all_emp_byid1(self,idemp):
        empid = str(str(idemp).replace('[','')).replace(']','')
        myemp = self.env['hr.employee'].sudo().browse(int(empid))
        empgroup = myemp.employee_group1
        datahr ={
              'emp_no': myemp.employee_id,
              'nik': myemp.nik,
              'employee_id':  myemp.id,
              'employee_name': myemp.name,
              'area': myemp.area.name,
              'bisnis_unit': myemp.department_id.branch_id.name,
              'departmetid': myemp.department_id.name,
              'jobstatus': myemp.job_status,
              'employementstatus':  myemp.emp_status,
              'jobtitle':  myemp.employee_levels.id,
              'empgroup':  empgroup,
        }
        return datahr