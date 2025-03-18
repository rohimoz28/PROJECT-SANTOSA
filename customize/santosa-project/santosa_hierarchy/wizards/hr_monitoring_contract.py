from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict
from datetime import datetime
date_format = "%Y-%m-%d"
class HrMonitoringContract(models.TransientModel):
    _name = 'hr.monitoring.contract'

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    @api.depends('area','bisnis_unit')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['sanhrms.department'].sudo().search([('branch_id','=', allrecs.bisnis_unit.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]

    area = fields.Many2one('res.territory',string='Area')
    branch_ids = fields.Many2many('res.branch','res_branch_rel',string='AllBranch',compute='_isi_semua_branch',store=False)
    alldepartment = fields.Many2many('sanhrms.department','hr_department_rel', string='All Department',compute='_isi_department_branch',store=False)
    job_status = fields.Selection([('permanent','Permanent'),
                                   ('contract','Contract'),
                                   ('outsource','Out Source')],string='Job Status')
    emp_status = fields.Selection([('probation','Probation'),
                                   ('confirmed','Confirmed'),
                                   ('probation', 'Probation'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('terminated', 'Terminated'),
                                   ],string='Employment Status')
    bisnis_unit = fields.Many2one('res.branch',string='Bussiness Unit',domain="[('id','in',branch_ids)]",tracking=True,)
    department_id = fields.Many2one('sanhrms.department',string='Department',domain="[('id','in',alldepartment)]")
    directorate_id = fields.Many2one('sanhrms.directorate',string='Directorate')
    division_id = fields.Many2one('sanhrms.division',string='Division')
    contractend_start = fields.Date('From')
    contractend_end = fields.Date('To')
    bsdate_from = fields.Date('From')
    bsdate_to = fields.Date('To')
    pension_start = fields.Date('From')
    pension_end = fields.Date('To')
    confirmed_start = fields.Date('From')
    confirmed_to = fields.Date('To')

    result_ids = fields.One2many('hr.monitoring.contractdetails','result_id',auto_join=True)


    def pencarian_data(self,area = False,bisnis_unit= False,job_status= False,emp_status= False,department_id= False,contractend_start= False,contract_dateto= False,bsdate_from= False,bsdate_to= False,pension_start= False,pension_date= False):
        for allrec in self:
            emp_status = allrec.emp_status
            mydet = self.env['hr.monitoring.contractdetails']
            mycari = allrec.sudo()
            empdata = False
            # pensiun_start_bak = False
            # pensiun_start = ''
            # pension_start =''
            # if pension_start:
            #     pensiun_start_bak = pension_start.split(':')[0]
            #     pensiun_start = pensiun_start_bak.replace('T00','')
            #     pension_start = pensiun_start
            # pensiun_end_bak = False
            # pensiun_end = False
            # pension_date = False
            # if pension_date:
            #     pensiun_end_bak = pension_date.split(':')[0]
            #     pensiun_end = pensiun_end_bak.replace('T00', '')
            #     pension_date = pensiun_end
            allrec.result_ids.unlink()
            # if not job_status:
            #     print('jobstatus ', job_status)
            #     if area and not bisnis_unit and not job_status and not department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('area', '=', area)])
            #         print('harusnya kemari ')
            #     elif area and bisnis_unit and not job_status and not department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('area', '=', area),('branch_id','=',bisnis_unit)])
            #     elif area and bisnis_unit and not job_status and department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('area', '=', area),('branch_id','=',bisnis_unit),('department_id','=',department_id)])
            #     elif not area and bisnis_unit and not job_status and not department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('branch_id','=',bisnis_unit)])
            #     elif not area and bisnis_unit and not job_status and not department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('department_id','=',department_id)])
            #     elif not area and not bisnis_unit and  job_status and not department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('job_status','=',job_status)])
            #     elif  area and not bisnis_unit and not job_status and department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('area','=',area),('department_id','=',department_id)])
            #     elif  area and  bisnis_unit and not job_status and not department_id and not emp_status and  not contractend_start and not contract_dateto and not pension_start and not pension_date:
            #         empdata = self.env['hr.employee'].sudo().search(
            #             [('area','=',area),('branch_id','=',bisnis_unit)])
            #
            #     if empdata:
            #         print('ketemu data ', allrec.bisnis_unit.name)
            #         for allemp in empdata:
            #             mydet |= self.env['hr.monitoring.contractdetails'].sudo().create({'result_id': allrec.id,
            #                                                                               'employee_id': allemp.id,
            #                                                                               'employeid': allemp.employee_id,
            #                                                                               'nik': allemp.nik,
            #                                                                               'department': allemp.department_id.name,
            #                                                                               'job_title': allemp.job_id.name,
            #                                                                               'job_status': allemp.job_status,
            #                                                                               'employe_status': allemp.emp_status,
            #                                                                               'end_contract': allemp.contract_dateto,
            #                                                                               'end_bsdate': False,
            #                                                                               'pension_date': allemp.pension_date})
            #
            # else:

            self.env['hr.monitoring.contractdetails'].sudo().search([]).unlink()
            caridata = False
            if job_status == 'permanent':
                pstart = str(pension_start).split('T')[0]
                pend = str(pension_date).split('T')[0]

                pension_start = ''
                pension_date = ''
                pension_start = pstart
                pension_date = pend
                p_start = datetime.strptime(str(pstart), date_format)
                p_date = datetime.strptime(str(pend), date_format)
                if area and not bisnis_unit and not department_id and not emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('job_status','=',job_status)])
                elif area and not bisnis_unit and  department_id and not emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('department_id','=',department_id),('job_status','=',job_status)])
                elif area and not bisnis_unit and  department_id and emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('department_id','=',department_id),('emp_status','=',emp_status),('job_status','=',job_status)])
                elif area and  bisnis_unit and  department_id and emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('branch_id','=',bisnis_unit),('department_id','=',department_id),('emp_status','=',emp_status),('job_status','=',job_status)])
                elif area and  bisnis_unit and  department_id and not emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('branch_id','=',bisnis_unit),('department_id','=',department_id),('job_status','=',job_status)])
                elif area and  bisnis_unit and  not department_id and  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('branch_id','=',bisnis_unit),('emp_status','=',emp_status),('job_status','=',job_status)])
                elif area and  bisnis_unit and  department_id and  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('branch_id','=',bisnis_unit),('department_id','=',department_id),('emp_status','=',emp_status),('job_status','=',job_status)])
                elif not area and  bisnis_unit and  department_id and  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('branch_id','=',bisnis_unit),('department_id','=',department_id),('emp_status','=',emp_status),('job_status','=',job_status)])
                elif not area and  bisnis_unit and  department_id and not  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('branch_id','=',bisnis_unit),('department_id','=',department_id),('job_status','=',job_status)])
                elif not area and  bisnis_unit and  not department_id and not  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('branch_id','=',bisnis_unit),('job_status','=',job_status)])
                elif not area and  bisnis_unit and   department_id and not  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('branch_id','=',bisnis_unit),('department_id','=',department_id),('job_status','=',job_status)])
                elif not area and  bisnis_unit and not  department_id and  emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('branch_id','=',bisnis_unit),('emp_status','=',emp_status),('job_status','=',job_status)])
                elif  area and  bisnis_unit and not  department_id and  not emp_status and  pension_start and  pension_date:
                    caridata = self.env['hr.employee'].sudo().search([('area','=',area),('branch_id','=',bisnis_unit),('job_status','=',job_status)])
                empdata = caridata.filtered(lambda op: op.pension_date >= p_start.date() and op.pension_date <= p_date.date())
                if empdata:
                    for allemp in empdata:
                        mydet |= self.env['hr.monitoring.contractdetails'].sudo().create({'result_id': allrec.id,
                                                                                          'employee_id': allemp.id,
                                                                                          'employeid': allemp.employee_id,
                                                                                          'nik': allemp.nik,
                                                                                          'department': allemp.department_id.name,
                                                                                          'job_title': allemp.job_id.name,
                                                                                          'job_status': allemp.job_status,
                                                                                          'employe_status': allemp.emp_status,
                                                                                          'end_contract': allemp.contract_dateto,
                                                                                          'end_bsdate': False,
                                                                                          'pension_date': allemp.pension_date})


            elif job_status == 'contract':
                cstart = str(contractend_start).split('T')[0]
                cend = str(contract_dateto).split('T')[0]
                contractend_start = ''
                contract_dateto = ''
                c_start = datetime.strptime(str(cstart), date_format)
                c_date = datetime.strptime(str(cend), date_format)
                contractend_start = cstart
                contract_dateto = cend
                if area and not bisnis_unit and not department_id and not emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('job_status', '=', job_status)])
                elif area and not bisnis_unit and not department_id and emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('job_status', '=', job_status),('emp_status','=',emp_status)])
                elif area and not bisnis_unit and  department_id and emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('job_status', '=', job_status),('emp_status','=',emp_status),('department_id','=',department_id)])
                elif area and not bisnis_unit and  department_id and not emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('job_status', '=', job_status),('department_id','=',department_id)])
                elif area and bisnis_unit and not department_id and not emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('branch_id', '=', bisnis_unit), ('job_status', '=', job_status)])
                elif area and bisnis_unit and not department_id and emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('branch_id', '=', bisnis_unit), ('job_status', '=', job_status),('emp_status','=',emp_status)])
                elif area and bisnis_unit and  department_id and emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('branch_id', '=', bisnis_unit), ('job_status', '=', job_status),('department_id','=',department_id),('emp_status','=',emp_status)])
                elif area and bisnis_unit and  department_id and not emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('area', '=', area), ('branch_id', '=', bisnis_unit), ('job_status', '=', job_status),('department_id','=',department_id)])
                elif not area and bisnis_unit and department_id and not emp_status:
                    caridata = self.env['hr.employee'].sudo().search(
                        [('department_id', '=', department_id), ('branch_id', '=', bisnis_unit), ('job_status', '=', job_status),
                          ('emp_status', '=', emp_status)])

                if caridata:
                    datasaring = caridata.filtered(lambda h: h.contract_datefrom != False or h.contract_dateto != False)
                    empdata = datasaring.filtered(
                        lambda kp: kp.contract_dateto >= c_start.date() and kp.contract_dateto <= c_date.date())
                    if empdata:
                        for allemp in empdata:
                            mydet |= self.env['hr.monitoring.contractdetails'].sudo().create({'result_id': allrec.id,
                                                                                              'employee_id': allemp.id,
                                                                                              'employeid': allemp.employee_id,
                                                                                              'nik': allemp.nik,
                                                                                              'department': allemp.department_id.name,
                                                                                              'job_title': allemp.job_id.name,
                                                                                              'job_status': allemp.job_status,
                                                                                              'employe_status': allemp.emp_status,
                                                                                              'end_contract': allemp.contract_dateto,
                                                                                              'end_bsdate': False,
                                                                                              'pension_date': allemp.pension_date})



            allrec.result_ids = mydet.ids
            return True

    def print_hasil(self):
        return True

class HrMonitoringContractDetails(models.TransientModel):
    _name = 'hr.monitoring.contractdetails'




    result_id = fields.Many2one('hr.monitoring.contract',string='Result ID', index=True)
    employee_id = fields.Many2one('hr.employee',string='Name')
    employeid = fields.Char( string='Employee #')
    nik = fields.Char(string='NIK')
    department = fields.Char(string='Department')
    job_title = fields.Char(string='Job Title')
    job_status = fields.Char(string='Job Status')
    employe_status = fields.Char(string='Employee Status')
    end_contract = fields.Date(string='End Of Contract')
    end_bsdate = fields.Date(string='End Of BS')
    pension_date = fields.Date(string='Pension Date')


