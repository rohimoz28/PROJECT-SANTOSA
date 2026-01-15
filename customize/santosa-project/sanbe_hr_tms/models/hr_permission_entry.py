# -*- coding : utf-8 -*-

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from pytz import timezone, UTC
from datetime import datetime, timedelta, time
from odoo.tools.misc import format_date


class HRPermissionEntry(models.Model):
    _name = "hr.permission.entry"
    _rec_name = 'trans_number'
    _description = 'HR Permission Entry'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    @api.depends('area_id', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id', '=', allrecs.branch_id.id),('active','=',True)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]

    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_ids = fields.Many2many('res.branch', 'hr_permission_entry_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    alldepartment = fields.Many2many('hr.department', 'hr_employeelist_schedule_rel', string='All Department', compute='_isi_department_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', domain="[('id','in',branch_ids)]", tracking=True,)
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    employee_id = fields.Many2one('hr.employee', domain="[('area','=',area_id),('branch_id','=',branch_id)]", string='Employee Name', index=True, tracking=True)
    directorate_id = fields.Many2one(comodel_name='sanhrms.directorate', related='employee_id.directorate_id', string='Directorate', index=True, store=True)
    hrms_department_id = fields.Many2one(comodel_name='sanhrms.department', related='employee_id.hrms_department_id', string='Department', index=True, store=True)
    job_id = fields.Many2one(comodel_name='hr.job', related='employee_id.job_id', string='Job Position', index=True, store=True)
    permission_date_from = fields.Date('Permission From')
    permission_date_To = fields.Date('Permission To')
    permission_status = fields.Selection(selection=[('draft', 'Draft'),
                                                    ('approved', "Approved"),
                                                    ('close','Close'),
                                                    ('cancel','Cancel')],
                                        string="Status", readonly=True, copy=False,
                                        index=True, tracking=3, default='draft')

    permission_time_from = fields.Float('Time From')
    permission_time_to = fields.Float('Time To')
    time_days = fields.Float('Time', compute='_get_days_duration') # re-create to accomodate table sb_leave_allocation
    time_hour = fields.Float('Hours',compute='_total_jam_ijin',store=False)
    handled_temp_to = fields.Many2one('hr.employee', string='Handled By')
    back_to_office = fields.Date('Back To Office')
    back_tooffice_time = fields.Float('Time')
    remarks = fields.Text('Remarks')
    doc_number = fields.Char('Ref Doc Number')
    trans_number = fields.Char('Transaction Number', default=lambda self: _('New'),
                               copy=False, readonly=True, tracking=True, requirement=True)
    approve1_by = fields.Many2one('hr.employee', string='Approved 1 By')
    approve1_job_title = fields.Many2one('hr.job', string='Job Title')
    approve2_by = fields.Many2one('hr.employee', string='Approved 2 By')
    approve2_job_title = fields.Many2one('hr.job', string='Job Title')
    approve3_by = fields.Many2one('hr.employee', string='Approved 3 By')
    approve3_job_title = fields.Many2one('hr.job', string='Job Title')
    is_holiday = fields.Boolean('Is Holiday', default=False)
    leave_id = fields.Many2one('hr.leave', string='Leaves ID',index=True)
    employee_company_id = fields.Many2one(related='employee_id.company_id', string="Employee Company", store=True)
    is_approved = fields.Boolean(default=False, string='is Approved')
    approved1 = fields.Boolean(default=False, string='Approved1')
    approved2 = fields.Boolean(default=False, string='Approved2')
    approved3 = fields.Boolean(default=False, string='Approved3')
    holiday_status_id = fields.Many2one("hr.leave.type", store=True, string="Permission Code",
                                        required=True, readonly=False, tracking=True)
    nik = fields.Char(related='employee_id.nik')
    leave_allocation_id = fields.Many2one('sb.leave.allocation', string='Leave Allocation ID', compute='_compute_leave_allocation_id')
    leave_allocation = fields.Float(string='Leave Allocation', related='leave_allocation_id.leave_remaining',
                                    readonly=True, store=True)
    permission_type_id = fields.Many2one('sb.leave.benefit', domain="[('leave_req_id.employee_id','=',employee_id)]", string='Permission Type')
    leave_used = fields.Float('Leave Used', compute='_compute_permission_type', store=True)
    total_leave_balance = fields.Float('Total Leave Balance', compute='_compute_permission_type', store=True)
    remaining_leave = fields.Float('Remaining Leave', compute='_compute_permission_type', store=True)

    @api.depends('permission_type_id', 'permission_date_from', 'permission_date_To')
    def _compute_permission_type(self):
        for rec in self:
            if rec.permission_type_id:
                rec.total_leave_balance = rec.permission_type_id.total_leave_balance
                rec.leave_used = rec.time_days
                rec.remaining_leave = max(rec.total_leave_balance - rec.leave_used, 0.0)
            else:
                rec.total_leave_balance = 0
                rec.leave_used = 0
                rec.remaining_leave = 0
    
    @api.constrains('leave_used','total_leave_balance')
    def _constrains_leave_balance(self):
        for rec in self:
            if rec.leave_used and rec.total_leave_balance and rec.leave_used > rec.total_leave_balance:
                raise ValidationError('Insufficient leave balance.')
    
    @api.constrains('total_leave_balance','permission_type_id')
    def _constraint_leave_balance_zero(self):
        for rec in self:
            if rec.permission_type_id and rec.total_leave_balance == 0:
                raise ValidationError('You cannot create a Permission Entry. Leave balance is 0.')

    @api.onchange('holiday_status_id', 'time_days')
    def set_remarks(self):
        for rec in self:
            if rec.holiday_status_id.id == 6 and rec.time_days:
                rec.remarks = f"CUTI {int(rec.time_days)} HARI"

    @api.depends('employee_id')
    def _compute_leave_allocation_id(self):
        for record in self:
            if record.employee_id:
                leave_allocation = self.env['sb.leave.allocation'].search([
                    ('employee_id', '=', record.employee_id.id)
                ], order='id desc', limit=1)
                record.leave_allocation_id = leave_allocation
            else:
                record.leave_allocation_id = False

    @api.depends('permission_date_from','permission_date_To')
    def _get_days_duration(self):
        date_format = "%Y-%m-%d"
        for rec in self:
            if rec.permission_date_To and rec.permission_date_from:
                ganti1 = rec.permission_date_To.strftime(date_format)
                ganti2 = rec.permission_date_from.strftime(date_format)
                tgl1 = datetime.strptime(ganti1, date_format)
                tgl2 = datetime.strptime(ganti2, date_format)
                total_days = (tgl1 - tgl2).days
                rec.time_days = total_days + 1
                #rec.time_days = (tgl1 - tgl2).days
            else:
                rec.time_days = 0

    @api.depends('permission_time_from','permission_time_to')
    def _total_jam_ijin(self):
        for allrec in self:
            if allrec.permission_time_from and allrec.permission_time_to:
                mytime = allrec.permission_time_to - allrec.permission_time_from
                allrec.time_hour = mytime
            else:
                allrec.time_hour = 0

    @api.onchange('employee_id')
    def isi_job_post(self):
        for recs in self:
            if not recs.employee_id:
                return
            recs.job_id = recs.employee_id.job_id.id
            recs.department_id = recs.employee_id.department_id.id
            recs.branch_id = recs.employee_id.branch_id.id

    def _validate_leave_alloc(self, employee, holiday_status_id, time_days):
        time_days += 1
        if holiday_status_id == 6:
            leave_alloc = self.env['sb.leave.allocation'].sudo().search([('employee_id', '=', employee)], limit=1)
            if not leave_alloc or leave_alloc.leave_remaining < time_days:
                raise ValidationError('Employee Has No Leave Allocation.\nPlease choose Leave Type: Unpaid Leave.')

    @api.model_create_multi
    def create(self, vals_list):
        
        for vals in vals_list:
            if vals.get('trans_number', _('New')) == _('New'):
                if 'area_id' in vals:
                    area_id = vals.get('area_id')
                    directorate_id = vals.get('directorate_id')
                    department_id = vals.get('hrms_department_id')
                    branch_id = vals.get('branch_id')
                    dt_area = self.env['res.territory'].browse(area_id) if area_id else False
                    dept = self.env['sanhrms.department'].browse(department_id) if department_id else False
                    branch = self.env['res.branch'].browse(branch_id) if branch_id else False
                    department_code = dept.department_code if dept else ''
                    branch_unit_id = branch.unit_id if branch else ''

                    if dt_area:
                        tgl = fields.Date.today()
                        tahun = str(tgl.year)[2:]
                        bulan = str(tgl.month)
                        # vals['trans_number'] = cdo + str(tahun) + str(self.env['ir.sequence'].next_by_code('hr.permission.entry'))
                        vals['trans_number'] = f"{tahun}/{bulan}/{branch_unit_id}/PE/{department_code}/{self.env['ir.sequence'].next_by_code('hr.permission.entry')}"
        res = super(HRPermissionEntry,self).create(vals_list)

        for alldata in res:
            #Search if data is holiday based on tmsentry data
            if not alldata.is_holiday:
                #Search if employee data already exist
                myleave = self.env['hr.leave'].sudo().search([('permition_id','=',alldata.id)])
                if not myleave:
                    #IF Hr Leave no Data Permition Id than created it
                    myleave = self.env['hr.leave'].sudo().create({'employee_id': alldata.employee_id.id,
                                                                  'date_from': alldata.permission_date_from,
                                                                  'date_to': alldata.permission_date_To,
                                                                  'request_date_from': alldata.permission_date_from,
                                                                  'request_date_to': alldata.permission_date_To,
                                                                  'number_of_days_display': alldata.permission_date_To - alldata.permission_date_from,
                                                                  'is_permition': True,
                                                                  'holiday_type': 'employee',
                                                                  'department_id': alldata.employee_id.department_id.id,
                                                                  'company_id': self.env.company.id,
                                                                  'holiday_status_id': alldata.holiday_status_id.id,
                                                                  'permition_id': alldata.id or alldata._origin.id})
                    alldata.leave_id = myleave.id
        return res
    
    @api.onchange('approved1','approved2','approved3')
    def set_approved_status(self):
        for allrec in self:
            # print('param 1 ',(allrec.approved1 == True and allrec.approved2 == True))
            # print('param 2 ',(allrec.approved1 == True and allrec.approved3 == True))
            # print('param 3 ',(allrec.approved2 == True and allrec.approved3 == True))
            if (allrec.approved1 == True and allrec.approved2 == True) or \
                (allrec.approved1 == True and allrec.approved3 == True) or \
                (allrec.approved2 == True and allrec.approved3 == True):
                allrec.is_approved = True
            else:
                allrec.is_approved = False

    @api.onchange('approve1_by')
    def set_approved_status1(self):
        for allrec in self:
            if not allrec.approve1_by:
               return
            allrec.approve1_job_title = allrec.approve1_by.job_id.id
            
    @api.onchange('approve2_by')
    def set_approved_status2(self):
        for allrec in self:
            if not allrec.approve2_by:
               return
            allrec.approve2_job_title = allrec.approve2_by.job_id.id
            
    @api.onchange('approve3_by')
    def set_approved_status3(self):
            for allrec in self:
                if not allrec.approve3_by:
                    return
                allrec.approve3_job_title = allrec.approve3_by.job_id.id

    def btn_approve(self):
        for rec in self:
            if rec.is_approved == True:
                rec.permission_status = 'approved'

                if rec.permission_type_id:
                    benefit = rec.permission_type_id
                    benefit.total_leave_balance = rec.remaining_leave

                    self.env['sb.leave.tracking'].create({  
                        'leave_req_id': benefit.leave_req_id.id,
                        'date': rec.permission_date_from,
                        'permission_date_from': rec.permission_date_from,
                        'permission_date_to': rec.permission_date_To,
                        'leave_master_id': benefit.leave_master_id.id,
                        'leave_allocation': rec.total_leave_balance,
                        'leave_used': rec.leave_used,
                        'leave_remaining': rec.remaining_leave,
                        'remarks': rec.remarks,
                        'permission_status': rec.permission_status
                    })

                if rec.permission_date_from and rec.permission_date_To:
                    # days_permission = (rec.permission_date_To - rec.permission_date_from).days
                    full_day_leave = rec.leave_allocation_id.leave_remaining - rec.time_days
                    half_day_leave = rec.leave_allocation_id.leave_remaining - 0.5
                    if rec.holiday_status_id.id == 6:
                        if rec.leave_allocation_id:
                            # rec.leave_allocation_id.leave_allocation -= days_permission + 1
                            new_leave_allocation = self.env['sb.leave.allocation'].create({'employee_id': rec.employee_id.id,
                                                                    'date': rec.permission_date_from,
                                                                    'area_id': rec.area_id.id,
                                                                    'branch_id': rec.branch_id.id,
                                                                    'job_id': rec.job_id.id,
                                                                    'department_id': rec.department_id.id,
                                                                    'leave_allocation': 0,
                                                                    'leave_used': rec.time_days,
                                                                    'leave_remaining': full_day_leave,
                                                                    'remarks': rec.remarks
                                                                    })
                            rec.leave_allocation_id = new_leave_allocation.id
                    elif rec.holiday_status_id.id == 7: 
                        if rec.leave_allocation_id:
                            # rec.leave_allocation_id.leave_allocation -= 0.5
                            new_leave_allocation = self.env['sb.leave.allocation'].create({'employee_id': rec.employee_id.id,
                                                                    'date': rec.permission_date_from,
                                                                    'area_id': rec.area_id.id,
                                                                    'branch_id': rec.branch_id.id,
                                                                    'job_id': rec.job_id.id,
                                                                    'department_id': rec.department_id.id,
                                                                    'leave_allocation': 0,
                                                                    'leave_used': 0.5,
                                                                    'leave_remaining': half_day_leave,
                                                                    'remarks': rec.remarks
                                                                    })
                            rec.leave_allocation_id = new_leave_allocation.id
                    else:
                        pass
            else:
                raise UserError('Need 2 Approver check List')
            
    def btn_draft(self):
        for rec in self:
            rec.permission_status = 'draft'
            
    def btn_close(self):
        for rec in self:
            rec.permission_status = 'done'

    def btn_cancel(self):
        for rec in self:
            rec.permission_status = 'cancel'

            if rec.permission_type_id:
                    benefit = rec.permission_type_id
                    benefit.total_leave_balance = rec.total_leave_balance

                    self.env['sb.leave.tracking'].create({  
                        'leave_req_id': benefit.leave_req_id.id,
                        'date': rec.permission_date_from,
                        'permission_date_from': rec.permission_date_from,
                        'permission_date_to': rec.permission_date_To,
                        'leave_master_id': benefit.leave_master_id.id,
                        'leave_allocation': rec.remaining_leave,
                        'leave_used': -abs(rec.leave_used),
                        'leave_remaining': rec.total_leave_balance,
                        'remarks': rec.remarks,
                        'permission_status': rec.permission_status
                    })

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
                          node.set('create', '0')
        return arch, view

    # restart running number
    def _reset_sequence_permission_entry(self):
        sequences = self.env['ir.sequence'].search([('code', '=like', '%permission.entry%')])
        sequences.write({'number_next_actual': 1})


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    permition_id = fields.Many2one('hr.permission.entry',string='Permission ID', index=True)
    is_permition = fields.Boolean('Is From Permition', default=False)

    #Function to create data permition
    @api.model_create_multi
    def create(self, vals_list):
        res = super(HolidaysRequest,self).create(vals_list)
        for alldata in res:
            #Search for flagging if not from permition than create permition data
            if not alldata.is_permition:
                #Search if permition entry already create with leave
                myleave = self.env['hr.permission.entry'].sudo().search([('leave_id','=',alldata.id)])
                if not myleave:
                    #IF permition dont have leave id than we create new one
                    myleave = self.env['hr.permission.entry'].sudo().create({'area_id': alldata.employee_id.area.id,
                                                                            'branch_id': alldata.employee_id.branch_id.id,
                                                                            'employee_id': alldata.employee_id.id,
                                                                            'permission_date_from': alldata.date_from,
                                                                            'permission_date_To': alldata.date_to,
                                                                            'leave_id': alldata.id or alldata._origin.id,
                                                                            'holiday_status_id': alldata.holiday_status_id.id,
                                                                            'is_holiday': True})
                    alldata.permition_id = myleave.id
        return res

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
                          node.set('create', '0')
        return arch, view