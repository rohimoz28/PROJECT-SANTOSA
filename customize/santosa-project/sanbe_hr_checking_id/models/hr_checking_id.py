# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class HRCheckingID(models.Model):
    _name = 'hr.checking.id'
    _description = 'HR Checking ID'

    noktp = fields.Char(string='KTP #')
    nonpwp = fields.Char(string='NPWP #')
    nonik = fields.Char(string='NIK #')
    nonik_lama = fields.Char(string='NIK Lama #')

    emp_no = fields.Char('Employee No')
    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    employee_name = fields.Char(string='Employee Name')
    nik = fields.Char('NIK')
    nik_lama = fields.Char('NIK Lama')
    area = fields.Char('Area')
    bisnis_unit = fields.Char('Unit Bisinis')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id')
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', related='employee_id.hrms_department_id')
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id')
    job_id = fields.Many2one('hr.job','Jabatan', related='employee_id.job_id', readonly=True)
    departmentid = fields.Char('Sub Department')
    jobstatus = fields.Char('Job Status')
    employementstatus = fields.Char('Employeement Status')
    jobtitle = fields.Char('Job Title')
    empgroup = fields.Char('Employee P Group')
    blacklist= fields.Boolean('Blacklist',default=False)
    end_of_contract = fields.Boolean('End Of Contract', default=False,store=True)


    def pencarian_data(self):
        return
    
    def aktivasi_data(self,enik=False):
        if not enik:
            enik = self.nik
        mut_id = False
        if enik:
            emp = self.env['hr.employee'].sudo().search([('nik','=',enik)],limit=1)
            mut = self.env['hr.employee.mutations'].sudo()
            if emp:
                mut_id = mut.create({
                    'employee_id' : emp.id,
                    'emp_id' : emp.employee_id,
                    'service_type' : 'actv',
                    'service_start' : fields.Date.today(),
                })
                
                mut_id._onchange_employee_id()
                mut_id.env.cr.commit()
        if mut_id:
            return mut_id.id
        #else:
        #    return {}
    
    @api.onchange('noktp','nonpwp','nonik','nonik_lama')
    def _isi_data(self):
        for allrec in self:
            dataemp = False
            # datatracking = False
            if allrec.noktp and not allrec.nonpwp and not allrec.nonik and not allrec.nonik_lama:
                dataemp = self.env['hr.employee'].sudo().search([('no_ktp', '=', allrec.noktp)], limit=1)
            elif not allrec.noktp  and allrec.nonpwp and not allrec.nonik and not allrec.nonik_lama:
                dataemp = self.env['hr.employee'].sudo().search([('no_npwp', '=', allrec.nonpwp)], limit=1)
            elif not allrec.noktp  and not allrec.nonpwp and not allrec.nonik and allrec.nonik_lama:
                dataemp = self.env['hr.employee'].sudo().search([('nik_lama', '=', allrec.nonik_lama)], limit=1)
            elif not allrec.noktp  and not allrec.nonpwp and allrec.nonik and not allrec.nonik_lama:
                dataemp = self.env['hr.employee'].sudo().search([('nik', '=', allrec.nonik)], limit=1)
            else:
                dataemp = self.env['hr.employee'].sudo().search([('no_npwp', '=', allrec.nonpwp), ('no_ktp', '=', allrec.noktp ), ('nik', '=', allrec.nonik ), ('nik_lama', '=', allrec.nonik_lama )], limit=1)

            datatracking = self.env['hr.employment.log'].sudo().search([('employee_id', '=', dataemp.id)], order='create_date desc', limit=1)
            
            if dataemp:
                datahr = {}
                empgroup =dataemp.employee_group1
                allrec.emp_no = dataemp.id
                allrec.employee_id = dataemp.id
                allrec.employee_name = dataemp.name
                allrec.nik = dataemp.nik
                allrec.nik_lama = dataemp.nik_lama
                allrec.area = dataemp.area.name
                allrec.bisnis_unit = dataemp.department_id.branch_id.name
                allrec.departmentid = dataemp.department_id.name
                allrec.jobstatus = dataemp.job_status
                allrec.employementstatus = dataemp.emp_status
                allrec.jobtitle = dataemp.job_id.name
                allrec.empgroup = empgroup
                if datatracking and datatracking.emp_status == 'end_contract':
                    allrec.end_of_contract = True
                else:
                    allrec.end_of_contract = False
            else:
                allrec.emp_no = ''
                allrec.employee_id = False
                allrec.employee_name = ''
                allrec.nik = ''
                allrec.nik_lama = ''
                allrec.area = ''
                allrec.bisnis_unit = ''
                allrec.departmentid = ''
                allrec.jobstatus = ''
                allrec.employementstatus = ''
                allrec.jobtitle = ''
                allrec.empgroup = ''
            #    raise UserError('Data Not Found')

    @api.model
    def cari_data_npwp_or_nik(self,resid, ktp=False,npwp=False,nik=False,nik_lama=False):
        dataemp = False
        if ktp and npwp == '' and nik == '' and nik_lama == '':
            dataemp = self.env['hr.employee'].sudo().search([('no_ktp','=', ktp)],limit=1)
        elif ktp == '' and npwp and nik == '' and nik_lama == '':
            dataemp = self.env['hr.employee'].sudo().search([('no_npwp','=',npwp)],limit=1)
        elif ktp == '' and npwp == '' and nik and nik_lama == '':
            dataemp = self.env['hr.employee'].sudo().search([('nik','=',nik)],limit=1)
        elif ktp == '' and npwp == '' and nik == '' and nik_lama:
            dataemp = self.env['hr.employee'].sudo().search([('nik_lama','=',nik_lama)],limit=1)
        else:
            dataemp = self.env['hr.employee'].sudo().search([('no_npwp','=',npwp),('no_ktp','=', ktp),('nik','=',nik),('nik_lama','=', nik_lama)],limit=1)
        if dataemp:
            datahr = {}
            empgroup = dataemp.employee_group1
            datahr = {
                'employee_id': [dataemp.id, dataemp.name],
                'employee_name': dataemp.name,
                'area': dataemp.area.name,
                'bisnis_unit': dataemp.department_id.branch_id.name,
                'departmentid': dataemp.department_id.name,
                'jobstatus': dataemp.job_status,
                'employementstatus': dataemp.emp_status,
                'jobtitle': dataemp.job_id.name,
                'empgroup': empgroup,
                'nik': dataemp.nik,
                'nik_lama': dataemp.nik_lama,
                #'no_npwp': dataemp.no_npwp
            }
            return datahr
        else:
            raise UserError("Dat@ Not Found")
