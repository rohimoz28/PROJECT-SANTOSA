
from odoo import fields, models, api, _, Command


class HrListEmployeeSchedule(models.TransientModel):
    _name = 'hr.employeelist.schedule'
    _description = 'Search Employee Schedule Wizard'

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id', '=', allrecs.branch_id.id),('active','=',True)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]

    area = fields.Many2one('res.territory',string='Area',tracking=True,)
    branch_ids = fields.Many2many('res.branch','hr_employeelist_schedule_rel',string='AllBranch',compute='_isi_semua_branch',store=False)
    alldepartment = fields.Many2many('hr.department','hr_employeelist_schedule_rel', string='All Department',compute='_isi_department_branch',store=False)
    branch_id = fields.Many2one('res.branch',string='Bussines Unit',domain="[('id','in',branch_ids)]",tracking=True,)
    department_id = fields.Many2one('hr.department',domain="[('id','in',alldepartment)]")
    employee_id = fields.Many2one('hr.employee',string='Employee ID',default='New')
    employee_list = fields.One2many('hr.employeelist.schedule_details','hr_list_id',auto_join=True,string='Employee List')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    

class HrListEmployeeScheduleDetails(models.TransientModel):
    _name = 'hr.employeelist.schedule_details'
    _description = 'Search Employee Schedule Details Wizard'

    hr_list_id = fields.Many2one('hr.employeelist.schedule',string='Employee List Id',index=True)
    department_id = fields.Many2one('hr.department',string='Department',index=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    nik = fields.Char('NIK')
    employee_id = fields.Many2one('hr.employee',string='Employee',index=True)
    job_id  = fields.Many2one('hr.job',string='Job Position',index=True)
    wd_code = fields.Char('WD Code')
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')



