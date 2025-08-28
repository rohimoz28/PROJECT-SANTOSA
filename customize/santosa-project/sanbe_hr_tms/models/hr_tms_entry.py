# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import pytz
from datetime import datetime,time, timedelta,date
TMS_ENTRY_STATE = [
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('reject', 'Reject'),
    ('done', 'Close'),
]

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    #Function For Filtter Branch Based On Area ID
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    @api.depends('area_id','branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            allwds = self.env['hr.working.days'].sudo().search([('area_id','=',allrecs.area_id.id),('available_for','in',allrecs.branch_id.ids),('is_active','=',True)])
            allrecs.wdcode_ids = [Command.set(allwds.ids)]
            
    def _default_employee(self):
        return self.env.user.employee_id

    @api.depends('ot_approve')
    def _cek_for_approved(self):
        for alldata in self:
            if alldata.ot_approve == True:
                alldata.sanbe_readytoapprove = True
            else:
                alldata.sanbe_readytoapprove = False

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False, tracking=True)
    check_out = fields.Datetime(string="Check Out", tracking=True)
    tmsentry_id = fields.Many2one('hr.tmsentry.summary',string='TMS Entry Summary',index=True)
    periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',related='tmsentry_id.periode_id',index=True)
    tmsentry_status = fields.Selection(related='tmsentry_id.state')
    emp_id = fields.Integer('Employees ID')
    employee_id =fields.Many2one('hr.employee', domain="[('branch_id','=',branch_id)]",string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True,)
    department_id = fields.Many2one('hr.department',related='employee_id.department_id',string='Sub Department',store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi',related='employee_id.division_id',store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen',related='employee_id.hrms_department_id', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat',related='employee_id.directorate_id',  store=True)
    area_id = fields.Many2one('res.territory',string='Area ID', index=True )
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel_tms_entry', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    branch_id = fields.Many2one('res.branch',string='Business Units',index=True,domain="[('id','in',branch_ids)]")
    job_id = fields.Many2one('hr.job',string='Job Title',related='employee_id.job_id')
    nik = fields.Char('NIK',related = 'employee_id.nik')
    day = fields.Char('Day')
    dates = fields.Date('Date', tracking=True)
    day_type = fields.Selection([('w','W'),
                                 ('h','H')],string='Type',default='w',index=True)
    wdcode_ids = fields.Many2many('hr.working.days','wd_tms_entry_rel',string='WD Code All',compute='_isi_department_branch', store=False)
    #wdcode_ids = fields.Many2many('hr.working.days','wd_tms_entry_rel',string='WD Code All')
    wdcode = fields.Many2one('hr.working.days',domain="[('id','in',wdcode_ids)]",string='WD Code',index=True)
    wdcode_edited = fields.Many2one('hr.working.days',domain="[('id','in',wdcode_ids)]",string='WD Code Edited',index=True)
    codes = fields.Many2one('hr.empgroup',string='WD',tracking=True)
    attendence_status = fields.Selection([('attendee','Attendee'),
                               ('sick','Sick'),
                               ('absent','Absent'),
                               ('delay_in','Delay In'),
                               ('leave','Leave'),
                               ('outstation','OutStation')],string='Attendence Status', tracking=True)
    time_in = fields.Float('Time In', tracking=True)
    time_out = fields.Float('Time Out', tracking=True)
    add_hour = fields.Float('Add Hour')
    ot1 = fields.Char('AOT1')
    ot2 = fields.Char('AOT2')
    ot3 = fields.Char('AOT3')
    ot4 = fields.Char('AOT4')
    ot_auto = fields.Char('AOT Auto')
    ot1_time = fields.Float('OT1 Timex')
    ot2_time = fields.Float('OT2 Timex')
    ot3_time = fields.Float('OT3 Timex')
    ot4_time = fields.Float('OT4 Timex')
    ot_auto_time = fields.Float('OT Autox')
    ot_autox = fields.Integer('AOT Auto')
    ot1_timex = fields.Integer('OT1 Time')
    ot2_timex = fields.Integer('OT2 Time')
    ot3_timex = fields.Integer('OT3 Time')
    ot4_timex = fields.Integer('OT4 Time')
    ot_auto_timex = fields.Integer('OT Auto')
    ot_approve = fields.Boolean('Approve',tracking=True)
    #ot2_approve = fields.Boolean('Approve',tracking=True)
    #ot3_approve = fields.Boolean('Approve',tracking=True)
    ot_status = fields.Char('OT Status')
    tms_status = fields.Selection(
        selection=TMS_ENTRY_STATE,
        string="TMS Entry Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    sanbe_readytoapprove = fields.Boolean('Ready TO Approved',compute='_cek_for_approved',store=False)
    tunjangan_trp = fields.Float('TRP')
    tunjagan_meal = fields.Float('Meal')
    delay_time = fields.Char('Delay')
    approve_ot_from1 = fields.Float('Approve OT From')
    approve_ot_from2 = fields.Float('Approve OT From')
    premi_attendee = fields.Float('Premi Attendee')
    night_shift = fields.Float('Night Shift')
    
    approved = fields.Boolean('Approved', tracking=True)
    ot_reject = fields.Boolean('OT Reject')
    wd_type = fields.Char('WD Type', tracking=True)
    hour_adv = fields.Float('Hour Adv')
    permision_code = fields.Char('Permision Code', tracking=True)
    plan_ot_from = fields.Float('Plan Overtime From', tracking=True)
    plan_ot_to = fields.Float('Plan Overtime To', tracking=True)
    time_in_edited = fields.Float('Time In (Edited)', tracking=True)
    time_out_edited = fields.Float('Time Out (Edited)', tracking=True)
    approval_ot_from = fields.Float('Approval Overtime From', tracking=True)
    approval_ot_to = fields.Float('Approval Overtime To', tracking=True)
    hour_adv1 = fields.Float('Hour Adv Edited')

    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('Valid To')
    delayed = fields.Float('Delay (jam:menit)', tracking=True)
    tms_entry_ot = fields.One2many('hr.tmsentry.details','tms_entry_id',auto_join=True)
    tms_entry_premi = fields.One2many('hr.tmsentry.premicode','tms_entry_id',auto_join=True)
    tgl_masuk = fields.Date('Date In', tracking=True)
    tgl_keluar = fields.Date('Date Out', tracking=True)
    att_time = fields.Float('Attendance Time')

    #def init(self):
    #    self.env.cr.execute("""ALTER TABLE hr_attendance DROP CONSTRAINT IF EXISTS hr_attendance_codes_fkey;""")
    #    self.env.cr.commit()
    
    def _getwaktu(self,waktu):
        ret = timedelta()
        for i in waktu:
            (h, m, s) = i.split(':')
            d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            ret += d
        return ret
    
    def _getwaktu2(self,waktu):
        ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m))
        ret += d
        return ret
    
    def _getwaktu4(self,waktu):
        ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        ret += d
        return ret
    
    def _getwaktu3(self,waktu):
        #ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        ret = self._getfloat(d)
        return ret
    
    def ubahjam(self,hours_float):
        midnight = datetime.combine(date.today(), time.min)
        time_delta = timedelta(hours=hours_float)
        time_obj = (midnight + time_delta).time()
        return time_obj

    def ubahjam2(self,waktu):
        detik = waktu * 3600
        hours = divmod(detik, 3600)[0] # split to hours and seconds
        sisad = detik - (hours * 3600)
        minutes = divmod(sisad,60)[0]
        seconds = sisad - (minutes * 60)
        #result = '{0:02.0f}:{1:02.0f}'.format(*divmod(waktu * 60, 60))
        result = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(hours, minutes, seconds)
        return result
    
    def _getjam(self,jam):
        ret = None
        detik = jam.total_seconds()
        hour = divmod(detik,3600)[0]
        sisad = detik - (hour * 3600)
        minute = divmod(sisad,60)[0]
        second = sisad - (minute * 60)
        ret = str(hour) + ":" + minute + ":" + second
        return ret
    
    def _getfloat(self,jam):
        ret = None
        detik = jam.total_seconds()
        hour = divmod(detik,3600)[0]
        minute = divmod(detik,3600)[1]/3600
        #hour = divmod(detik,3600)[0]
        #sisad = detik - (hour * 3600)
        #minute = divmod(sisad,60)[0]
        #second = sisad - (minute * 60)
        ret = hour + minute
        return ret
        
    def btn_reject(self):
        for rec in self:
            rec.tms_status = 'reject'
            rec.ot_reject = True

    def btn_done(self):
        for rec in self:
            rec.tms_status = 'done'

    def btn_approved(self):
        for rec in self:
            rec.approved = True

    @api.model
    def default_get(self, default_fields):
        #super it
        res = super(HrAttendance, self).default_get(default_fields)
        myempid = self._context.get('employee_id')
        if myempid:
            #if there is context for employee id then fill emp_id from context
            res['emp_id'] = myempid
        return res

    @api.onchange('employee_id')
    def isi_employee(self):
        #Wee fill employee data based on employee_id
        for allrec in self:
            if not allrec.employee_id:
                return
            #Fill all neccessary data from employee_id data
            allrec.nik = allrec.employee_id.nik
            allrec.department_id = allrec.employee_id.department_id.id
            allrec.job_id = allrec.employee_id.job_id.id
            allrec.area_id  = allrec.employee_id.area.id
            allrec.branch_id = allrec.employee_id.branch_id.id

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)

    def ambil_view(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'name':'hr attendance',
                'view_mode': 'form',
                'views': [[self.env.ref('sanbe_hr_tms.hr_tmsentry_form_ext').id, 'form']],
                'res_model': 'hr.attendance',
                'res_id': rec.id,
                'target': 'current',
                'context': {'create': False, 'delete': False, 'edit' : True},
            }
    
    @api.model
    def approved_data_all(self,resID):
        if resID:
            datatms = self.env['hr.attendance'].sudo().search([('id','=',resID)])
            if datatms:
                datatms.write({
                    'tms_status' : 'approved',
                    'ot_approve' : True,
                    'ot_status' : 'All OT Approved'
                })
        return #{'type': 'ir.actions.client','tag': 'reload'}
        
    def approved_data(self):
        self.ensure_one()
        self.tms_status = 'approved'
        self.ot_approve = True
        self.ot_status = 'All OT Approved'

    def transfer_payroll(self):
        return self.write({'tms_status': 'done'})

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

    def action_calculation(self):
        for alldata in self:
            if alldata.tms_status == 'approved':
                return
            
            if not alldata.time_in or not alldata.time_out:
                # Cek Permission
                perm = self.env['hr.permission.entry'].sudo().search([('employee_id','=',alldata.employee_id.id),('permission_date_from','<=',alldata.dates),('permission_date_To','>=',alldata.dates)],limit=1)
                    
                if perm:
                    alldata.attendence_status = False
                    scode = perm.holiday_status_id.code
                    alldata.permision_code = scode
                    if scode == 'SICK':
                        alldata.attendence_status = 'sick'
                    if scode == 'HLEA':
                        alldata.attendence_status = 'leave'
                    if scode == 'UN2':
                        alldata.attendence_status = 'delay_in'
                    if scode == 'LEAV':
                        alldata.attendence_status = 'outstation'
                else:    
                    return
                
            if alldata.time_in_edited:
                jammasuk1 = datetime.strptime(str(alldata.ubahjam(alldata.time_in_edited)).replace(' ', ''), '%H:%M:%S')
                #jammasuk1 = alldata.ubahjam(alldata.time_in_edited)
                jammasuk = jammasuk1.strftime('%H:%M:%S')
            else:
                if alldata.time_in:    
                    jammasuk1 = datetime.strptime(str(alldata.ubahjam(alldata.time_in)).replace(' ', ''), '%H:%M:%S')
                    #jammasuk1 = alldata.ubahjam(alldata.time_in)
                    jammasuk = jammasuk1.strftime('%H:%M:%S')
                else:
                    jammasuk = False
            
            if alldata.time_out_edited: 
                jamkeluar1 = datetime.strptime(str(alldata.ubahjam(alldata.time_out_edited)).replace(' ', ''), '%H:%M:%S')
                #jamkeluar1 = alldata.ubahjam(alldata.time_out_edited)
                jamkeluar = jamkeluar1.strftime('%H:%M:%S')
            else:
                if alldata.time_out:
                    jamkeluar1 = datetime.strptime(str(alldata.ubahjam(alldata.time_out)).replace(' ', ''), '%H:%M:%S')
                    #jamkeluar1 = alldata.ubahjam(alldata.time_out)
                    jamkeluar = jamkeluar1.strftime('%H:%M:%S')
                else:
                    jamkeluar = False
            
            if jammasuk and jamkeluar:
                alldata.attendence_status = 'attendee'
                
            wd = False
            if alldata.wdcode_edited:
                wd = alldata.wdcode_edited
            else:
                wd = alldata.wdcode
                
            if wd:
                if (alldata.time_in_edited or alldata.time_in) and (alldata.time_out_edited or alldata.time_out):
                    perm = self.env['hr.permission.entry'].sudo().search([('employee_id','=',alldata.employee_id.id),('permission_date_from','<=',alldata.dates),('permission_date_To','>=',alldata.dates)],limit=1)
                    if perm:
                        scode = perm.holiday_status_id.code
                        alldata.permision_code = scode

                        if scode == 'SICK':
                            alldata.attendence_status = 'sick'
                        if scode == 'HLEA':
                            alldata.attendence_status = 'leave'
                        if scode == 'UN2':
                            alldata.attendence_status = 'delay_in'
                        if scode == 'LEAV':
                            alldata.attendence_status = 'outstation'
                            
                    
                    # print('===================')
                    # print('tanggal',alldata.dates)
                    # print('Employee',alldata.employee_id.name)
                    # print('jam masuk edit',alldata.time_in_edited)
                    # print('jam masuk edit konversi',alldata.ubahjam(alldata.time_in_edited))
                    # print('jam masuk',alldata.time_in)
                    # print('jam masuk konversi',alldata.ubahjam(alldata.time_in))
                    # print('jam keluar edit',alldata.time_out_edited)
                    # print('jam keluar edit konversi',alldata.ubahjam(alldata.time_out_edited))
                    # print('jam keluar',alldata.time_out)
                    # print('jam keluar konversi',alldata.ubahjam(alldata.time_out))
                    # print('===================')
                    
                    stimefrom1 = datetime.strptime(str(alldata.ubahjam(wd.fullday_from)).replace(' ', ''), '%H:%M:%S')
                    #stimefrom1 = alldata.ubahjam(wd.fullday_from)
                    stimefrom = stimefrom1.strftime('%H:%M:%S')
                    
                    stimeto1 = datetime.strptime(str(alldata.ubahjam(wd.fullday_to)).replace(' ', ''), '%H:%M:%S')
                    #stimeto1 = alldata.ubahjam(wd.fullday_to)
                    stimeto = stimeto1.strftime('%H:%M:%S')
                    
                    #Clean all field calculate
                    alldata.ot1 = False
                    alldata.ot1_time = False
                    alldata.ot2 = False
                    alldata.ot2_time = False
                    alldata.ot3 = False
                    alldata.ot3_time = False
                    alldata.ot4 = False
                    alldata.ot4_time = False
                    alldata.ot_auto = False
                    alldata.ot_auto_time = False
                    #alldata.codes = False
                    alldata.att_time = False
                    alldata.add_hour = False
                    alldata.night_shift = False
                    alldata.delayed = False
                    alldata.premi_attendee = False
                    alldata.tunjangan_trp = False
                    
                    alldata.ot1_timex = False
                    alldata.ot2_timex = False
                    alldata.ot3_timex = False
                    alldata.ot4_timex = False
                    alldata.ot_auto_timex = False
                    
                    alldata.wd_type = False
                    alldata.hour_adv = False
                    alldata.permision_code = False
                    alldata.tunjagan_meal = False
                    alldata.plan_ot_from = False
                    alldata.plan_ot_to = False
                    alldata.valid_from = False
                    alldata.valid_to = False
                    alldata.approval_ot_from = False
                    alldata.approval_ot_to = False
                        
                    alldata.wd_type = wd.code
                    
                    dtkeluar = datetime.strptime(str(alldata.tgl_keluar) + ' ' + str(jamkeluar),'%Y-%m-%d %H:%M:%S')
                    dtmasuk = datetime.strptime(str(alldata.tgl_masuk) + ' ' + str(jammasuk),'%Y-%m-%d %H:%M:%S')
                    dtjmasuk = datetime.strptime(str(alldata.dates) + ' ' + str(stimefrom),'%Y-%m-%d %H:%M:%S')
                    dtjkeluar = datetime.strptime(str(alldata.dates) + ' ' + str(stimeto),'%Y-%m-%d %H:%M:%S')
                    delayt = 0
                    delay = 0

                    if jammasuk and jamkeluar:
                        if dtkeluar > dtjkeluar:
                            if dtmasuk <= dtjmasuk:
                                alldata.add_hour = alldata._getfloat(dtkeluar - dtjkeluar)
                            else:
                                alldata.add_hour = False
                                
                            if dtmasuk < dtjmasuk:
                                alldata.att_time = alldata._getfloat(dtjkeluar - dtjmasuk)
                            else:
                                alldata.att_time = alldata._getfloat(dtjkeluar - dtmasuk)
                        else:
                            alldata.add_hour = False
                            if dtmasuk < dtjmasuk:
                                alldata.att_time = alldata._getfloat(dtkeluar - dtjmasuk)
                            else:
                                alldata.att_time = alldata._getfloat(dtkeluar - dtmasuk)
                    else:
                        alldata.att_time = False
                        alldata.add_hour = False
                            
                    if dtmasuk > dtjmasuk:
                        delayt = alldata._getfloat(dtmasuk - dtjmasuk)
                        delay = (dtmasuk - dtjmasuk).total_seconds()
                    
                    if delay > 0:
                        if alldata.attendence_status == 'delay_in':
                            alldata.delayed = False
                        else:
                            if divmod(delay,60)[0] > wd.delay_allow:
                                alldata.delayed = delayt
                            else:
                                alldata.delayed = False
                    else:
                        alldata.delayed = False
                    
                    if len(wd.allowance_ids) > 0:
                        tshift = 0
                        ttrans = 0
                        tatten = 0
                        tmeal = 0
                        if alldata.time_out_edited:
                            tout = alldata.time_out_edited
                        else:
                            tout = alldata.time_out
                        
                        if alldata.time_in_edited:
                            tin = alldata.time_in_edited
                        else:
                            tin = alldata.time_in
                        
                        if alldata.employee_id.attende_premie == True:
                            print('--------------------')
                            print(tin)
                            print(tout)
                            print(wd.id)
                            sql = """
                                select qty from hr_allowance_list hal 
                                where hal.workingday_id={wdid} and hal.code ='ashf'
                                    and (hal.time_from >= {masuk} and hal.time_to <= {keluar})
                                order by qty desc,time_from asc
                            """.format(wdid=wd.id,masuk=tin,keluar=tout)
                            self.env.cr.execute(sql)
                            allow_att = self.env.cr.fetchone()
                            #allow_att = wd.allowance_ids.filtered(lambda p: p.code == 'ashf' and p.time_from >= tin and p.time_to <= tout)
                            print(allow_att)
                            #print(allow_att[0])
                            print('--------------------')
                            ##for allow in wd.allowance_ids.filtered(lambda p: p.code == 'ashf'):
                            ##asfrom1 = datetime.strptime(str(alldata.ubahjam(allow.time_from)).replace(' ', ''), '%H:%M:%S')
                            ##asfrom1 = alldata.ubahjam(allow.time_from)
                            #asfrom = asfrom1.strftime('%H:%M:%S')
                            #asto1 = datetime.strptime(str(alldata.ubahjam(allow.time_to)).replace(' ', ''), '%H:%M:%S')
                            ##asto1 = alldata.ubahjam(allow.time_to)
                            #asto = asto1.strftime('%H:%M:%S')
                            #asqty = allow.qty
                            #if dtmasuk <= asfrom1 and dtkeluar >= asto1:
                            if allow_att or allow_att is not None:
                                tatten = float(allow_att[0])
                            
                        if alldata.employee_id.allowance_transport == True:
                            #allow_trans = wd.allowance_ids.filtered(lambda p: p.code == 'atrp' and (tin <= p.time_from and tout >= p.time_to))
                            sql = """
                                select qty from hr_allowance_list hal 
                                where hal.workingday_id={wdid} and hal.code ='atrp'
                                    and (hal.time_from >= {masuk} and hal.time_to <= {keluar})
                                order by qty desc,time_from asc
                            """.format(wdid=wd.id,masuk=tin,keluar=tout)
                            self.env.cr.execute(sql)
                            allow_trans = self.env.cr.fetchone()
                            if allow_trans or allow_trans is not None:
                                ttrans = float(allow_trans[0])
                            #if allow.code == 'atrp':
                            #    atfrom1 = datetime.strptime(str(alldata.ubahjam(allow.time_from)).replace(' ', ''), '%H:%M:%S')
                            #    #atfrom1 = alldata.ubahjam(allow.time_from)
                            #    atfrom = atfrom1.strftime('%H:%M:%S')
                            #    atto1 = datetime.strptime(str(alldata.ubahjam(allow.time_to)).replace(' ', ''), '%H:%M:%S')
                            #    #atto1 = alldata.ubahjam(allow.time_to)
                            #    atto = atto1.strftime('%H:%M:%S')
                            #    atqty = allow.qty
                            #    if dtmasuk <= atfrom1 and dtkeluar >= atto1:
                            #        ttrans += atqty
                                    
                        if alldata.employee_id.allowance_night_shift == True:
                            #allow_night = wd.allowance_ids.filtered(lambda p: p.code == 'ansf' and (tin <= p.time_from and tout >= p.time_to))
                            sql = """
                                select qty from hr_allowance_list hal 
                                where hal.workingday_id={wdid} and hal.code ='ansf'
                                    and (hal.time_from >= {masuk} and hal.time_to <= {keluar})
                                order by qty desc,time_from asc
                            """.format(wdid=wd.id,masuk=tin,keluar=tout)
                            self.env.cr.execute(sql)
                            allow_night = self.env.cr.fetchone()
                            if allow_night or allow_night is not None:
                                tshift = float(allow_night[0])
                            #if allow.code == 'ansf':
                            #    anfrom1 = datetime.strptime(str(alldata.ubahjam(allow.time_from)).replace(' ', ''), '%H:%M:%S')
                            #    #anfrom1 = alldata.ubahjam(allow.time_from)
                            #    anfrom = anfrom1.strftime('%H:%M:%S')
                            #    anto1 = datetime.strptime(str(alldata.ubahjam(allow.time_to)).replace(' ', ''), '%H:%M:%S')
                            #    #anto1 = alldata.ubahjam(allow.time_to)
                            #    anto = anto1.strftime('%H:%M:%S')
                            #    atqty = allow.qty
                            #    if dtmasuk <= anfrom1 and dtkeluar >= anto1:
                            #        tshift += atqty
                                    
                        if alldata.employee_id.allowance_meal == True:
                            #allow_meal = wd.allowance_ids.filtered(lambda p: p.code == 'amea' and (tin <= p.time_from and tout >= p.time_to))
                            sql = """
                                select qty from hr_allowance_list hal 
                                where hal.workingday_id={wdid} and hal.code ='amea'
                                    and (hal.time_from >= {masuk} and hal.time_to <= {keluar})
                                order by qty desc,time_from asc
                            """.format(wdid=wd.id,masuk=tin,keluar=tout)
                            self.env.cr.execute(sql)
                            allow_meal = self.env.cr.fetchone()
                            if allow_meal or allow_meal is not None:
                                tmeal = float(allow_meal[0])
                            #if allow.code == 'amea':
                            #    amfrom1 = datetime.strptime(str(alldata.ubahjam(allow.time_from)).replace(' ', ''), '%H:%M:%S')
                            #    #amfrom1 = alldata.ubahjam(allow.time_from)
                            #    amfrom = amfrom1.strftime('%H:%M:%S')
                            #    amto1 = datetime.strptime(str(alldata.ubahjam(allow.time_to)).replace(' ', ''), '%H:%M:%S')
                            #    #amto1 = alldata.ubahjam(allow.time_to)
                            #    amto = amto1.strftime('%H:%M:%S')
                            #    atqty = allow.qty
                            #    if dtmasuk <= amfrom1 and dtkeluar >= amto1:
                            #        tmeal += atqty
                                    
                        alldata.premi_attendee = tatten
                        alldata.night_shift = tshift
                        alldata.tunjangan_trp = ttrans
                        alldata.tunjagan_meal = tmeal
                            
                    if alldata.employee_id.allowance_ot == True:
                        data_ot = self.env['hr.overtime.planning'].sudo().search([('area_id','=',alldata.area_id.id),('branch_id','=',alldata.branch_id.id),('periode_from','<=',alldata.dates),('periode_to','>=',alldata.dates)])
                        if wd.type_hari != 'hday':
                            plan_ot_emp = data_ot.hr_ot_planning_ids.filtered(lambda p: p.employee_id.id == alldata.employee_id.id and (p.plann_date_from <= alldata.dates and p.plann_date_to >= alldata.dates) and p.ot_type == 'regular')
                        else:
                            plan_ot_emp = data_ot.hr_ot_planning_ids.filtered(lambda p: p.employee_id.id == alldata.employee_id.id and (p.plann_date_from <= alldata.dates and p.plann_date_to >= alldata.dates) and p.ot_type == 'holiday')
                        
                        if plan_ot_emp:
                            if len(wd.overtime_ids) > 0:
                                otcnt = 1
                                jmlot1 = 0
                                FMT = '%H:%M:%S'
                                datadetails = []
                                if len(alldata.tms_entry_ot) > 0:
                                    alldata.tms_entry_ot.unlink()
                                
                                for xx in plan_ot_emp:
                                    plan_ot_from1 = datetime.strptime(str(alldata.ubahjam(xx.approve_time_from)).replace(' ', ''), '%H:%M:%S')
                                    #plan_ot_from1 = alldata.ubahjam(xx.approve_time_from)
                                    plan_ot_from = plan_ot_from1.strftime('%H:%M:%S')
                                    plan_ot_to1 = datetime.strptime(str(alldata.ubahjam(xx.approve_time_to)).replace(' ', ''), '%H:%M:%S')
                                    #plan_ot_to1 = alldata.ubahjam(xx.approve_time_to)
                                    plan_ot_to = plan_ot_to1.strftime('%H:%M:%S')
                                    potmasuk = datetime.strptime(str(alldata.dates) + ' ' + str(plan_ot_from),'%Y-%m-%d %H:%M:%S')
                                    potkeluar = datetime.strptime(str(alldata.dates) + ' ' + str(plan_ot_to),'%Y-%m-%d %H:%M:%S')
                                    selplan =  divmod((potkeluar - potmasuk).total_seconds(),3600)[0]
                                    sisaplan = selplan
                                    ao_from = xx.approve_time_from
                                    ao_to = xx.approve_time_to
                                    po_from = xx.ot_plann_from
                                    po_to = xx.ot_plann_to
                                    hit = 1
                                    if len(wd.overtime_ids)>0:
                                        cek = False
                                        for allshift in wd.overtime_ids:
                                            if sisaplan > 0:
                                                otfrom1 = datetime.strptime(str(alldata.ubahjam(allshift.ot_from)).replace(' ', ''), '%H:%M:%S')
                                                #otfrom1 = alldata.ubahjam(allshift.ot_from)
                                                otfrom = otfrom1.strftime('%H:%M:%S')
                                                otto1 = datetime.strptime(str(alldata.ubahjam(allshift.ot_to)).replace(' ', ''), '%H:%M:%S')
                                                #otto1 = alldata.ubahjam(allshift.ot_to)
                                                otto = otto1.strftime('%H:%M:%S')
                                                otcodes = allshift.ot_code
                                                ottype = allshift.ot_type
                                                
                                                dtotmasuk1 = datetime.strptime(str(alldata.dates) + ' ' + str(otfrom),'%Y-%m-%d %H:%M:%S')
                                                if otto > otfrom:
                                                    dtotkeluar1 = datetime.strptime(str(alldata.dates) + ' ' + str(otto),'%Y-%m-%d %H:%M:%S')
                                                else:
                                                    dtotkeluar1 = datetime.strptime(str(alldata.dates + timedelta(days=1)) + ' ' + str(otto),'%Y-%m-%d %H:%M:%S')
                                                
                                                if cek == False:
                                                    selwd =  divmod((dtotkeluar1 - dtotmasuk1).total_seconds(),3600)[0]
                                                else:
                                                    selwd =  divmod((dtotkeluar1 - dtotmasuk1).total_seconds(),3600)[0]
                                                
                                                if hit ==1:
                                                    dtotmasuk = potmasuk
                                                    if selwd <= sisaplan:
                                                        dtotkeluar = dtotmasuk +  timedelta(hours=selwd)
                                                    else:
                                                        dtotkeluar = dtotmasuk +  timedelta(hours=sisaplan)
                                                else:
                                                    dtotmasuk = dtotkeluar   
                                                    if selwd <= sisaplan:
                                                        dtotkeluar = dtotmasuk +  timedelta(hours=selwd)
                                                    else:
                                                        dtotkeluar = dtotmasuk +  timedelta(hours=sisaplan)
                                                        
                                                selisiht = False
                                                selisih = 0
                                                selisihr = 0
                                                
                                                if dtkeluar >= dtotkeluar:
                                                    selisiht = alldata._getfloat(dtotkeluar - dtotmasuk)
                                                    selisih = (dtotkeluar - dtotmasuk).total_seconds()
                                                else:
                                                    if dtkeluar > dtotmasuk:
                                                        selisiht = alldata._getfloat(dtkeluar - dtotmasuk)
                                                        selisih = (dtkeluar - dtotmasuk).total_seconds()
                                                    else:
                                                        selisiht = False
                                                        selisih = 0
                                                
                                                if selisih > 0:
                                                    selisihr = divmod(selisih,3600)[0]
                                                else:
                                                    selisihr = 0
                                                
                                                if selisih > 0 and cek == False:
                                                    if ottype == 'regular' or ottype == 'holiday':
                                                        alldata.write({'ot' + str(otcodes)[(-1):]: otcodes, 'ot' + str(otcodes)[(-1):] + '_time': selisiht, 'ot' + str(otcodes)[(-1):] + '_timex': selisihr,'plan_ot_from':po_from,'plan_ot_to':po_to,'approval_ot_from':ao_from,'approval_ot_to':ao_to})

                                                    if ottype == 'automatic':
                                                        alldata.write({'ot_auto' : otcodes, 'ot_auto_time': selisiht, 'ot_auto_timex': selisihr})
                                                    
                                                    datadetails.append((0, 0, {'code_ot': otcodes, 'system_calch': selisiht, 'system_calcx': selisihr}))
                                                    if sisaplan > selwd:          
                                                        sisaplan = sisaplan - selwd
                                                        cek=False
                                                    else:
                                                        sisaplan = sisaplan
                                                        cek = True          
                                        alldata.sudo().write({'tms_entry_ot': datadetails})
            return 

    def clean_data(self):
        for rec in self:
            att = self.env['hr.attendance'].sudo()
            emps = att.search([('employee_id','=',rec.employee_id.id),('periode_id','=',self.periode_id.id)])
            if emps:
                emps.sudo().write({
                    'time_in' : False,
                    'time_out' : False,
                    'tgl_masuk' : False,
                    'tgl_keluar' : False,
                    'attendence_status' : False,
                })
class HRTMSEntryDetails(models.Model):
    _name = "hr.tmsentry.details"
    _description = 'HR TMS Entry Details'

    tms_entry_id = fields.Many2one('hr.attendance',string='TMS Entry')
    tmsentry_status = fields.Selection(related='tms_entry_id.tmsentry_status')
    code_ot = fields.Char('Code OT')
    system_calcx = fields.Integer('System Calc')
    system_calch = fields.Float('System Calch')
    edited = fields.Integer('Edited')
    approval = fields.Boolean('Approval')

class HRTMSEntryPremiCode(models.Model):
    _name = "hr.tmsentry.premicode"
    _description = 'HR TMS Entry Premi Code'

    tms_entry_id = fields.Many2one('hr.attendance',string='TMS Entry')
    tmsentry_status = fields.Selection(related='tms_entry_id.tmsentry_status')
    code_premi = fields.Char('Premi Code')
    approval = fields.Boolean('Approval')