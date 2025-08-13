# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError
from odoo.osv import expression
import pytz
import datetime
from datetime import datetime,time
from odoo.exceptions import MissingError, UserError
TMS_PROCESSING_ENTRY_STATE = [
    ('draft', 'Draft'),
    ('done', "Done"),
]
class HRTmsProcessing(models.Model):
    _name = "hr.tms.processing"
    _description = 'HR TMS Processing'

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
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id','=', allrecs.branch_id.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]

    area_id = fields.Many2one('res.territory',string='Area ID', index=True)
    #date_from = fields.Date(string='Date From')
    #date_to = fields.Date(string='To')
    alldepartment = fields.Many2many('hr.department','hr_department_emp_set_rel', string='All Department',compute='_isi_department_branch',store=False)
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee No')
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True, domain="[('id','in',branch_ids)]")
    #periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True, domain="[('isopen','=',True)]")
    state = fields.Selection(
        selection=TMS_PROCESSING_ENTRY_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    tmsentry_count = fields.Integer(string="TMS Entry Count", compute='_get_tms_entry',store=False)
    tmsentry_ids = fields.One2many('hr.attendance','tmsprocessing_id',auto_join=True ,readonly="state =='done'")

    @api.depends('tmsentry_ids','state')
    def _get_tms_entry(self):
        #Search all data in tms entry ids and fill tmsentry_count and tmsentry_ids
        for order in self:
            myentry = self.env['hr.attendance'].sudo().search([('tmsprocessing_id','=',order.id or order._origin.id)])
            order.tmsentry_ids = myentry.ids or []
            order.tmsentry_count = len(myentry)

    def btn_done(self):
        for rec in self:
            rec.state = 'done'
    
    def btn_open(self):
        for rec in self:
            rec.state = 'draft'
                    
    #Function to process data
    def process_data(self):
        for alldata in self:
            if alldata.employee_id:
                period = self.env['hr.opening.closing'].sudo().search([('state_process','=','running'),('isopen','=',True)])
            elif alldata.department_id and alldata.area_id and alldata.branch_id:
                period = self.env['hr.opening.closing'].sudo().search([('branch_id','=',alldata.branch_id.id),('area_id','=',alldata.area_id.id),('state_process','=','running'),('isopen','=',True)])    
            elif alldata.branch_id and alldata.area_id and not alldata.department_id:
                period = self.env['hr.opening.closing'].sudo().search([('branch_id','=',alldata.branch_id.id),('area_id','=',alldata.area_id.id),('state_process','=','running'),('isopen','=',True)])
                #myentry = self.env['hr.attendance'].sudo().search([('branch_id','=',alldata.branch_id.id),('dates','>=',alldata.date_from),('dates','<=',alldata.date_to)])
            elif alldata.area_id and not alldata.branch_id and not alldata.department_id:
                period = self.env['hr.opening.closing'].sudo().search([('area_id','=',alldata.area_id.id),('state_process','=','running'),('isopen','=',True)])
            for rexx in period:
                myentryx = self.env['hr.attendance'].sudo().search([('periode_id','=',rexx.id)])
                if myentryx:
                    if alldata.employee_id:
                        myentry = myentryx.filtered(lambda p: p.employee_id.id == alldata.employee_id.id)
                    elif alldata.department_id and alldata.area_id and alldata.branch_id:
                        myentry = myentryx.filtered(lambda p: p.department_id.id == alldata.department_id.id)
                    elif alldata.branch_id and alldata.area_id and not alldata.department_id:
                        myentry = myentryx.filtered(lambda p: p.branch_id.id == alldata.branch_id.id and p.area_id.id == alldata.area_id.id)
                    elif alldata.area_id and not alldata.branch_id and not alldata.department_id:
                        myentry = myentryx.filtered(lambda p: p.area_id.id == alldata.area_id.id)
                    
                    for rec in myentry:
                        rec.action_calculation()
                        rec.env.cr.commit()
                        rec.write({'tmsprocessing_id': alldata.id or alldata._origin.id})
                
    #def process_dataxxxx(self):
    #    #Avoid to singleton error
    #    for alldata in self:
    #        #If data exist == department id and not employee_id then
    #        if alldata.department_id and not alldata.employee_id:
    #            #search tms entry exist for department id and dates in range of date_from and date_to in processing form
    #            myentry = self.env['hr.attendance'].sudo().search([('department_id','=',alldata.department_id.id),('dates','>=',alldata.date_from),('dates','<=',alldata.date_to)])
    #            #for all data that exist in tms entry we looping from here
    #            for allentry in myentry:
    #                #set flagging if it attendee is for later used if the option status in tms entry is attendee if not then check for permition
    #                isattende = False
    #                if allentry.attendence_status == 'attendee':
    #                    #if the status of data tms entry is attendee then we set the flagg for attendee
    #                    isattende == True
    #                    mygroup = self.env['hr.empgroup.details'].sudo().search(
    #                        [('department_id', '=', allentry.employee_id.department_id.id)])
    #                    myid = []
    #                    for allsgrps in mygroup:
    #                        myid.append(allsgrps.empgroup_id.id)
    #                    # search for employee has working day
    #                    myworkingday = self.env['hr.empgroup'].sudo().search([('id', 'in', myid)])
    #                    idwd = False
    #                    for allwd in myworkingday:
    #                        if allwd.valid_from and allwd.valid_to:
    #                            # if there is valid working day that employee have beem setting up
    #                            if allentry.dates >= allwd.valid_from and allentry.dates <= allwd.valid_to:
    #                                idwd = allwd.id
    #                                break
    #                    myworkingday = self.env['hr.empgroup'].browse(idwd)
    #                    myvalid = myworkingday #.filtered(lambda xd:  allentry.dates <= xd.valid_from  and xd.valid_to <= allentry.dates)
    #                    if myvalid:
    #                        myholiday = self.env['resource.calendar.leaves'].sudo().search([('area_id','=',allentry.area_id.id),('branch_id','=',allentry.branch_id.id)])
    #                        isholiday = False
    #                        for allholi in myholiday:
    #                            datetime_from = datetime.strptime(str(allholi.date_from).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            datetime_to = datetime.strptime(str(allholi.date_to).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            tglan = datetime.strptime(str(allentry.dates),
    #                                                             "%Y-%m-%d")
    #                            if tglan>= datetime_from and tglan <= datetime_to:
    #                                isholiday = True
    #                                break
    #                        hariaktifvalid = False
    #                        # if myot:
    #                        myabsense = datetime.strptime(str(allentry.dates), '%Y-%m-%d')
    #                        hariabsen = myabsense.strftime('%A')
    #                        hariaktifawal = myvalid.working_day_from
    #                        hariaktifakhir = myvalid.working_day_to
    #                        daytoint = False
    #                        if hariabsen == 'Sunday':
    #                            daytoint = 0
    #                        elif hariabsen == 'Monday':
    #                            daytoint = 1
    #                        elif hariabsen == 'Tuesday':
    #                            daytoint = 2
    #                        elif hariabsen == ' Wednesday':
    #                            daytoint = 3
    #                        elif hariabsen == 'Thursday':
    #                            daytoint = 4
    #                        elif hariabsen == 'Friday':
    #                            daytoint = 5
    #                        elif hariabsen == 'Saturday':
    #                            daytoint = 6
    #                        if daytoint >= int(hariaktifawal) and daytoint <= int(hariaktifakhir):
    #                            hariaktifvalid = True
    #                        if hariaktifvalid == True and isholiday == True:
    #                            timein1 = str(allentry.time_in).split(':')[0]
    #                            timein2 = str(allentry.time_in).split(':')[1]
    #                            timein3 = str(allentry.time_in).split(':')[2]
    #                            timeins = time(int(timein1), int(timein2), int(timein3))
    #                            timeout1 = str(allentry.time_out).split(':')[0]
    #                            timeout2 = str(allentry.time_out).split(':')[1]
    #                            timeout3 = str(allentry.time_out).split(':')[2]
    #                            timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                            timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                            timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                            mytime = timesouts - timesins
    #                            # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                            tothour = 0
    #                            if str(mytime).find('day') != -1:
    #                                tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                            else:
    #                                tothour = int(str(mytime).split(':')[0])
    #                            fdfrom1 = str(myvalid.fullday_from).split(':')[0]
    #                            fdfrom2 = str(myvalid.fullday_from).split(':')[1]
    #                            fdfrom3 = str(myvalid.fullday_from).split(':')[2]
    #                            fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                            fdto1 = str(myvalid.fullday_to).split(':')[0]
    #                            fdto2 = str(myvalid.fullday_to).split(':')[1]
    #                            fdto3 = str(myvalid.fullday_to).split(':')[2]
    #                            fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                            fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                            fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                            myworkinghour = fullsdaysto - fullsdaysfrom
    #                            myworkinghours = 0
    #                            if str(myworkinghour).find('day') != -1:
    #                                myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                            else:
    #                                myworkinghours = int(str(myworkinghour).split(':')[0])
    #                            dataots =[]
    #                            if tothour > myworkinghours:
    #                                myot = self.env['hr.overtime.list'].sudo().search([('workingday_id','=', myvalid.code.id)])
    #                                for allots in myot:
    #                                   if allots.ot_from and allots.ot_to:
    #                                        otfrom1 = str(allots.ot_from).split(':')[0]
    #                                        otfrom2 = str(allots.ot_from).split(':')[1]
    #                                        otfrom3 = str(allots.ot_from).split(':')[2]
    #                                        otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                        otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                        otto1 = str(allots.ot_to).split(':')[0]
    #                                        otto2 = str(allots.ot_to).split(':')[1]
    #                                        otto3 = str(allots.ot_to).split(':')[2]
    #                                        otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                        ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                        if timesouts >= otfroms:
    #                                            dataots.append({'timein': otfroms,
    #                                                            'timeout': ottos,
    #                                                            'mytimeout': timesouts,
    #                                                            'totalhour': timesouts - otfroms,
    #                                                            'othour': ottos - otfroms,
    #                                                            'ottipes': allots.ot_type})
    #                                if len(dataots) == 1:
    #                                    allentry.write({'ot1': dataots['ottipes'],
    #                                                   'ot1_time': dataots['totalhour'],
    #                                                    'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                                elif len(dataots) >1:
    #                                    cnt = 1
    #                                    for alldataots in dataots:
    #                                        if cnt ==1:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot1': alldataots['ottipes'],
    #                                                                'ot1_time': alldataots['timeout']- alldataots['timein']})
    #                                        elif cnt== 2:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': alldataots['timeout']- alldataots['timein']})
    #                                            else:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': timesouts - alldataots['timein']})
    #                                        else:
    #                                            allentry.write({'ot3': alldataots['ottipes'],
    #                                                            'ot3_time': timesouts - alldataots['timein']})
#
    #                                        cnt +=1
    #                                    allentry.write({'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                        elif hariaktifvalid == True and isholiday == False:
    #                            timein1 = str(allentry.time_in).split(':')[0]
    #                            timein2 = str(allentry.time_in).split(':')[1]
    #                            timein3 = str(allentry.time_in).split(':')[2]
    #                            timeins = time(int(timein1), int(timein2), int(timein3))
    #                            timeout1 = str(allentry.time_out).split(':')[0]
    #                            timeout2 = str(allentry.time_out).split(':')[1]
    #                            timeout3 = str(allentry.time_out).split(':')[2]
    #                            timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                            timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                            timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                            mytime = timesouts - timesins
    #                            # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                            tothour = 0
    #                            if str(mytime).find('day') != -1:
    #                                tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                            else:
    #                                tothour = int(str(mytime).split(':')[0])
    #                            fdfrom1 = str(myvalid.fullday_from).split(':')[0]
    #                            fdfrom2 = str(myvalid.fullday_from).split(':')[1]
    #                            fdfrom3 = str(myvalid.fullday_from).split(':')[2]
    #                            fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                            fdto1 = str(myvalid.fullday_to).split(':')[0]
    #                            fdto2 = str(myvalid.fullday_to).split(':')[1]
    #                            fdto3 = str(myvalid.fullday_to).split(':')[2]
    #                            fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                            fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                            fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                            myworkinghour = fullsdaysto - fullsdaysfrom
    #                            myworkinghours = 0
    #                            if str(myworkinghour).find('day') != -1:
    #                                myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                            else:
    #                                myworkinghours = int(str(myworkinghour).split(':')[0])
    #                            dataots =[]
    #                            if tothour > myworkinghours:
    #                                myot = self.env['hr.overtime.list'].sudo().search([('workingday_id','=', myvalid.code.id)])
    #                                for allots in myot:
    #                                   if allots.ot_from and allots.ot_to:
    #                                        otfrom1 = str(allots.ot_from).split(':')[0]
    #                                        otfrom2 = str(allots.ot_from).split(':')[1]
    #                                        otfrom3 = str(allots.ot_from).split(':')[2]
    #                                        otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                        otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                        otto1 = str(allots.ot_to).split(':')[0]
    #                                        otto2 = str(allots.ot_to).split(':')[1]
    #                                        otto3 = str(allots.ot_to).split(':')[2]
    #                                        otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                        ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                        if timesouts >= otfroms:
    #                                            dataots.append({'timein': otfroms,
    #                                                            'timeout': ottos,
    #                                                            'mytimeout': timesouts,
    #                                                            'totalhour': timesouts - otfroms,
    #                                                            'othour': ottos - otfroms,
    #                                                            'ottipes': allots.ot_type})
    #                                if len(dataots) == 1:
    #                                    allentry.write({'ot1': dataots['ottipes'],
    #                                                   'ot1_time': dataots['totalhour'],
    #                                                    'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                    })
#
    #                                elif len(dataots) >1:
    #                                    cnt = 1
    #                                    for alldataots in dataots:
    #                                        if cnt ==1:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot1': alldataots['ottipes'],
    #                                                                'ot1_time': alldataots['timeout']- alldataots['timein'],
    #                                                                'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                                })
    #                                        elif cnt== 2:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': alldataots['timeout']- alldataots['timein']})
    #                                            else:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': timesouts - alldataots['timein']})
    #                                        else:
    #                                            allentry.write({'ot3': alldataots['ottipes'],
    #                                                            'ot3_time': timesouts - alldataots['timein']})
#
    #                                        cnt +=1
#
    #                        else:
    #                            allentry.write({'ot1': 'Holiday'})
    #                            timein1 = str(allentry.time_in).split(':')[0]
    #                            timein2 = str(allentry.time_in).split(':')[1]
    #                            timein3 = str(allentry.time_in).split(':')[2]
    #                            timeins = time(int(timein1), int(timein2), int(timein3))
    #                            timeout1 = str(allentry.time_out).split(':')[0]
    #                            timeout2 = str(allentry.time_out).split(':')[1]
    #                            timeout3 = str(allentry.time_out).split(':')[2]
    #                            timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                            timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                            timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                            mytime = timesouts - timesins
    #                            tothour = 0
    #                            if str(mytime).find('day') != -1:
    #                                tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                            else:
    #                                tothour = str(mytime)
    #                            allentry.write({'ot1_time': tothour, 'tmsprocessing_id': alldata.id or alldata._origin.id})
#
    #                    else:
    #                        myholiday = self.env['resource.calendar.leaves'].sudo().search([('area_id','=',allentry.area_id.id),('branch_id','=',allentry.branch_id.id)])
    #                        isholiday = False
    #                        for allholi in myholiday:
    #                            datetime_from = datetime.strptime(str(allholi.date_from).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            datetime_to = datetime.strptime(str(allholi.date_to).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            tglan = datetime.strptime(str(allentry.dates),
    #                                                             "%Y-%m-%d")
    #                            if tglan>= datetime_from and tglan <= datetime_to:
    #                                isholiday = True
    #                                break
    #                        myabsense = datetime.strptime(str(allentry.dates),'%Y-%m-%d')
    #                        hariabsen = myabsense.strftime('%A')
    #                        mywd = self.env['hr.working.days'].sudo().search([('area_id','=',allentry.area_id.id),('branch_id','=',allentry.branch_id.id)])
    #                        if mywd:
    #                            hariaktifvalid = False
    #                            if len(mywd) ==1:
    #                                hariaktifawal = mywd.working_day_from
    #                                hariaktifakhir = mywd.working_day_to
    #                                if not hariaktifawal or not hariaktifakhir:
    #                                    raise UserError ("There Is No Valid Working Days For Employee %s" %(allentry.employee_id.display_name))
    #                                myabsense = datetime.strptime(str(allentry.dates), '%Y-%m-%d')
    #                                hariabsen = myabsense.strftime('%A')
    #                                daytoint = False
    #                                if hariabsen == 'Sunday':
    #                                    daytoint = 0
    #                                elif hariabsen == 'Monday':
    #                                    daytoint = 1
    #                                elif hariabsen == 'Tuesday':
    #                                    daytoint = 2
    #                                elif hariabsen == ' Wednesday':
    #                                    daytoint = 3
    #                                elif hariabsen == 'Thursday':
    #                                    daytoint = 4
    #                                elif hariabsen == 'Friday':
    #                                    daytoint = 5
    #                                elif hariabsen == 'Saturday':
    #                                    daytoint = 6
    #                                if daytoint >= int(hariaktifawal) and daytoint <= int(hariaktifakhir):
    #                                    hariaktifvalid = True
    #                                if hariaktifvalid == True and isholiday == True:
    #                                    timein1 = str(allentry.time_in).split(':')[0]
    #                                    timein2 = str(allentry.time_in).split(':')[1]
    #                                    timein3 = str(allentry.time_in).split(':')[2]
    #                                    timeins = time(int(timein1), int(timein2), int(timein3))
    #                                    timeout1 = str(allentry.time_out).split(':')[0]
    #                                    timeout2 = str(allentry.time_out).split(':')[1]
    #                                    timeout3 = str(allentry.time_out).split(':')[2]
    #                                    timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                                    timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                                    timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                                    mytime = timesouts - timesins
    #                                    # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                                    tothour = 0
    #                                    if str(mytime).find('day') != -1:
    #                                        tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        tothour = int(str(mytime).split(':')[0])
    #                                    fdfrom1 = str(mywd.fullday_from).split(':')[0]
    #                                    fdfrom2 = str(mywd.fullday_from).split(':')[1]
    #                                    fdfrom3 = str(mywd.fullday_from).split(':')[2]
    #                                    fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                                    fdto1 = str(mywd.fullday_to).split(':')[0]
    #                                    fdto2 = str(mywd.fullday_to).split(':')[1]
    #                                    fdto3 = str(mywd.fullday_to).split(':')[2]
    #                                    fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                                    fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                                    fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                                    myworkinghour = fullsdaysto - fullsdaysfrom
    #                                    myworkinghours = 0
    #                                    if str(myworkinghour).find('day') != -1:
    #                                        myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        myworkinghours = int(str(myworkinghour).split(':')[0])
    #                                    dataots = []
    #                                    if tothour > myworkinghours:
    #                                        myot = self.env['hr.overtime.list'].sudo().search(
    #                                            [('workingday_id', '=', mywd.code.id)])
    #                                        for allots in myot:
    #                                            if allots.ot_from and allots.ot_to:
    #                                                otfrom1 = str(allots.ot_from).split(':')[0]
    #                                                otfrom2 = str(allots.ot_from).split(':')[1]
    #                                                otfrom3 = str(allots.ot_from).split(':')[2]
    #                                                otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                                otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                                otto1 = str(allots.ot_to).split(':')[0]
    #                                                otto2 = str(allots.ot_to).split(':')[1]
    #                                                otto3 = str(allots.ot_to).split(':')[2]
    #                                                otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                                ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                                if timesouts >= otfroms:
    #                                                    dataots.append({'timein': otfroms,
    #                                                                    'timeout': ottos,
    #                                                                    'mytimeout': timesouts,
    #                                                                    'totalhour': timesouts - otfroms,
    #                                                                    'othour': ottos - otfroms,
    #                                                                    'ottipes': allots.ot_type})
    #                                        if len(dataots) == 1:
    #                                            allentry.write({'ot1': dataots['ottipes'],
    #                                                            'ot1_time': dataots['totalhour'],
    #                                                            'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                            })
    #                                        elif len(dataots) > 1:
    #                                            cnt = 1
    #                                            for alldataots in dataots:
    #                                                if cnt == 1:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot1': alldataots['ottipes'],
    #                                                                        'ot1_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein'],
    #                                                                        'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                                                elif cnt == 2:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein'],
    #                                                                        'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                                                    else:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': timesouts - alldataots[
    #                                                                            'timein']})
    #                                                else:
    #                                                    allentry.write({'ot3': alldataots['ottipes'],
    #                                                                    'ot3_time': timesouts - alldataots['timein']})
#
    #                                                cnt += 1
    #                                elif hariaktifvalid == True and isholiday == False:
    #                                    timein1 = str(allentry.time_in).split(':')[0]
    #                                    timein2 = str(allentry.time_in).split(':')[1]
    #                                    timein3 = str(allentry.time_in).split(':')[2]
    #                                    timeins = time(int(timein1), int(timein2), int(timein3))
    #                                    timeout1 = str(allentry.time_out).split(':')[0]
    #                                    timeout2 = str(allentry.time_out).split(':')[1]
    #                                    timeout3 = str(allentry.time_out).split(':')[2]
    #                                    timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                                    timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                                    timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                                    mytime = timesouts - timesins
    #                                    # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                                    tothour = 0
    #                                    if str(mytime).find('day') != -1:
    #                                        tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        tothour = int(str(mytime).split(':')[0])
    #                                    fdfrom1 = str(mywd.fullday_from).split(':')[0]
    #                                    fdfrom2 = str(mywd.fullday_from).split(':')[1]
    #                                    fdfrom3 = str(mywd.fullday_from).split(':')[2]
    #                                    fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                                    fdto1 = str(mywd.fullday_to).split(':')[0]
    #                                    fdto2 = str(mywd.fullday_to).split(':')[1]
    #                                    fdto3 = str(mywd.fullday_to).split(':')[2]
    #                                    fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                                    fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                                    fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                                    myworkinghour = fullsdaysto - fullsdaysfrom
    #                                    myworkinghours = 0
    #                                    if str(myworkinghour).find('day') != -1:
    #                                        myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        myworkinghours = int(str(myworkinghour).split(':')[0])
    #                                    dataots = []
    #                                    if tothour > myworkinghours:
    #                                        myot = self.env['hr.overtime.list'].sudo().search(
    #                                            [('workingday_id', '=', mywd.id)])
    #                                        for allots in myot:
    #                                            if allots.ot_from and allots.ot_to:
    #                                                otfrom1 = str(allots.ot_from).split(':')[0]
    #                                                otfrom2 = str(allots.ot_from).split(':')[1]
    #                                                otfrom3 = str(allots.ot_from).split(':')[2]
    #                                                otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                                otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                                otto1 = str(allots.ot_to).split(':')[0]
    #                                                otto2 = str(allots.ot_to).split(':')[1]
    #                                                otto3 = str(allots.ot_to).split(':')[2]
    #                                                otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                                ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                                if timesouts >= otfroms:
    #                                                    dataots.append({'timein': otfroms,
    #                                                                    'timeout': ottos,
    #                                                                    'mytimeout': timesouts,
    #                                                                    'totalhour': timesouts - otfroms,
    #                                                                    'othour': ottos - otfroms,
    #                                                                    'ottipes': allots.ot_type})
    #                                        if len(dataots) == 1:
    #                                            allentry.write({'ot1': dataots['ottipes'],
    #                                                            'ot1_time': dataots['totalhour'],
    #                                                            'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                            })
    #                                        elif len(dataots) > 1:
    #                                            cnt = 1
    #                                            for alldataots in dataots:
    #                                                if cnt == 1:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot1': alldataots['ottipes'],
    #                                                                        'ot1_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein'],
    #                                                                        'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                                        })
    #                                                elif cnt == 2:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein']})
    #                                                    else:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': timesouts - alldataots[
    #                                                                            'timein']})
    #                                                else:
    #                                                    allentry.write({'ot3': alldataots['ottipes'],
    #                                                                    'ot3_time': timesouts - alldataots['timein']})
#
    #                                                cnt += 1
    #                                else:
    #                                    timein1 = str(allentry.time_in).split(':')[0]
    #                                    timein2 = str(allentry.time_in).split(':')[1]
    #                                    timein3 = str(allentry.time_in).split(':')[2]
    #                                    timeins = time(int(timein1), int(timein2), int(timein3))
    #                                    timeout1 = str(allentry.time_out).split(':')[0]
    #                                    timeout2 = str(allentry.time_out).split(':')[1]
    #                                    timeout3 = str(allentry.time_out).split(':')[2]
    #                                    timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                                    timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                                    timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                                    mytime = timesouts - timesins
    #                                    tothour = 0
    #                                    if str(mytime).find('day') != -1:
    #                                        tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        tothour = str(mytime)
    #                                    allentry.write({'ot1': str('Holiday'),
    #                                                    'ot1_time': str(tothour),
    #                                                    'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                    })
#
    #                        else:
    #                            raise UserError("There is no Employee Groups Or Working Days Found for area = %s , bisnis_unit = %s and employee =%s !" %(allentry.area_id.name, allentry.branch_id.name, allentry.employee_id.display_name))
#
    #                else:
    #                    #if the tms entry not attendee then we search for the existing permition off the employee
    #                    mypermition = self.env['hr.permission.entry'].sudo().search([('employee_id','=',allentry.employee_id.id)])
    #                    haspermition = False
    #                    for allpermition in mypermition:
    #                        if allpermition.permission_date_from and allpermition.permission_date_To:
    #                            if allentry.dates >= allpermition.permission_date_from  and allentry.dates <= allpermition.permission_date_To:
    #                                haspermition = allpermition.id
#
    #                                break
    #                    if haspermition:
    #                        tmspermition = self.env['hr.permission.entry'].sudo().browse(haspermition)
    #                        #if exist the permition then set the flagg of attende to True for later used
    #                        isattende == True
    #                        if allentry.attendence_status == 'sick':
    #                            #if the attendence_status is sick check for working day or employee group
    #                            mygroup = self.env['hr.empgroup.details'].sudo().search(
    #                                [('department_id', '=', allentry.employee_id.department_id.id)])
    #                            myid = []
    #                            for allsgrps in mygroup:
    #                                myid.append(allsgrps.empgroup_id.id)
    #                            #search for employee has working day
    #                            myworkingday = self.env['hr.empgroup'].sudo().search([('id', 'in', myid)])
    #                            idwd = False
    #                            for allwd in myworkingday:
    #                                if allwd.valid_from and allwd.valid_to:
    #                                    #if there is valid working day that employee have beem setting up
    #                                    if allentry.dates >= allwd.valid_from and allentry.dates <= allwd.valid_to:
    #                                        idwd = allwd.id
    #                                        break
    #                            if tmspermition.permission_status =='approved2' or tmspermition.permission_status =='approved3':
    #                                #Found the working day for the employee
    #                                myworkingday = self.env['hr.empgroup'].browse(idwd)
    #                                #if the attendence_status in the tms entry =='sick' so we just set the tms entry time in and time out to the working day time in and time out
    #                                allentry.write({'time_in': myworkingday.fullday_from,
    #                                                'time_out': myworkingday.fullday_to,
    #                                                'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                })
    #                            else:
    #                                allentry.write({'time_in': '00:00:00',
    #                                                'time_out': '00:00:00',
    #                                                'attendence_status': 'absent',
    #                                                'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                })
    #                        elif allentry.attendence_status == 'leave':
    #                            mygroup = self.env['hr.empgroup.details'].sudo().search(
    #                                [('department_id', '=', allentry.employee_id.department_id.id)])
    #                            myid = []
    #                            for allsgrps in mygroup:
    #                                myid.append(allsgrps.empgroup_id.id)
    #                            #search for employee has working day
    #                            myworkingday = self.env['hr.empgroup'].sudo().search([('id', 'in', myid)])
    #                            idwd = False
    #                            for allwd in myworkingday:
    #                                if allwd.valid_from and allwd.valid_to:
    #                                    #if there is valid working day that employee have beem setting up
    #                                    if allentry.dates >= allwd.valid_from and allentry.dates <= allwd.valid_to:
    #                                        idwd = allwd
    #                                        break
    #                            #Found the working day for the employee
    #                            myworkingday = self.env['hr.empgroup'].browse(idwd)
    #                            allentry.write({
    #                                            'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                            })
    #                    else:
    #                        allentry.write({'attendence_status':'absent',
    #                                        'time_in': '00:00:00',
    #                                        'time_out': '00:00:00',
    #                                        'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                        })
#
#
    #        elif not alldata.department_id and alldata.employee_id:
    #            myentry = self.env['hr.attendance'].sudo().search([('employee_id','=',alldata.employee_id.id),('dates','>=',alldata.date_from),('dates','<=',alldata.date_to)])
    #            #for all data that exist in tms entry we looping from here
    #            for allentry in myentry:
    #                #set flagging if it attendee is for later used if the option status in tms entry is attendee if not then check for permition
    #                isattende = False
    #                if allentry.attendence_status == 'attendee':
    #                    #if the status of data tms entry is attendee then we set the flagg for attendee
    #                    isattende == True
    #                    mygroup = self.env['hr.empgroup.details'].sudo().search(
    #                        [('department_id', '=', allentry.employee_id.department_id.id)])
    #                    myid = []
    #                    for allsgrps in mygroup:
    #                        myid.append(allsgrps.empgroup_id.id)
    #                    # search for employee has working day
    #                    myworkingday = self.env['hr.empgroup'].sudo().search([('id', 'in', myid)])
    #                    idwd = False
    #                    for allwd in myworkingday:
    #                        if allwd.valid_from and allwd.valid_to:
    #                            # if there is valid working day that employee have beem setting up
    #                            if allentry.dates >= allwd.valid_from and allentry.dates <= allwd.valid_to:
    #                                idwd = allwd.id
    #                                break
    #                    myworkingday = self.env['hr.empgroup'].browse(idwd)
    #                    myvalid = myworkingday #.filtered(lambda xd:  allentry.dates <= xd.valid_from  and xd.valid_to <= allentry.dates)
    #                    if myvalid:
    #                        myholiday = self.env['resource.calendar.leaves'].sudo().search([('area_id','=',allentry.area_id.id),('branch_id','=',allentry.branch_id.id)])
    #                        isholiday = False
    #                        for allholi in myholiday:
    #                            datetime_from = datetime.strptime(str(allholi.date_from).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            datetime_to = datetime.strptime(str(allholi.date_to).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            tglan = datetime.strptime(str(allentry.dates),
    #                                                             "%Y-%m-%d")
    #                            if tglan>= datetime_from and tglan <= datetime_to:
    #                                isholiday = True
    #                                break
    #                        hariaktifvalid = False
    #                        # if myot:
    #                        myabsense = datetime.strptime(str(allentry.dates), '%Y-%m-%d')
    #                        hariabsen = myabsense.strftime('%A')
    #                        hariaktifawal = myvalid.working_day_from
    #                        hariaktifakhir = myvalid.working_day_to
    #                        daytoint = False
    #                        if hariabsen == 'Sunday':
    #                            daytoint = 0
    #                        elif hariabsen == 'Monday':
    #                            daytoint = 1
    #                        elif hariabsen == 'Tuesday':
    #                            daytoint = 2
    #                        elif hariabsen == ' Wednesday':
    #                            daytoint = 3
    #                        elif hariabsen == 'Thursday':
    #                            daytoint = 4
    #                        elif hariabsen == 'Friday':
    #                            daytoint = 5
    #                        elif hariabsen == 'Saturday':
    #                            daytoint = 6
    #                        if daytoint >= int(hariaktifawal) and daytoint <= int(hariaktifakhir):
    #                            hariaktifvalid = True
    #                        if hariaktifvalid == True and isholiday == True:
    #                            timein1 = str(allentry.time_in).split(':')[0]
    #                            timein2 = str(allentry.time_in).split(':')[1]
    #                            timein3 = str(allentry.time_in).split(':')[2]
    #                            timeins = time(int(timein1), int(timein2), int(timein3))
    #                            timeout1 = str(allentry.time_out).split(':')[0]
    #                            timeout2 = str(allentry.time_out).split(':')[1]
    #                            timeout3 = str(allentry.time_out).split(':')[2]
    #                            timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                            timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                            timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                            mytime = timesouts - timesins
    #                            # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                            tothour = 0
    #                            if str(mytime).find('day') != -1:
    #                                tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                            else:
    #                                tothour = int(str(mytime).split(':')[0])
    #                            fdfrom1 = str(myvalid.fullday_from).split(':')[0]
    #                            fdfrom2 = str(myvalid.fullday_from).split(':')[1]
    #                            fdfrom3 = str(myvalid.fullday_from).split(':')[2]
    #                            fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                            fdto1 = str(myvalid.fullday_to).split(':')[0]
    #                            fdto2 = str(myvalid.fullday_to).split(':')[1]
    #                            fdto3 = str(myvalid.fullday_to).split(':')[2]
    #                            fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                            fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                            fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                            myworkinghour = fullsdaysto - fullsdaysfrom
    #                            myworkinghours = 0
    #                            if str(myworkinghour).find('day') != -1:
    #                                myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                            else:
    #                                myworkinghours = int(str(myworkinghour).split(':')[0])
    #                            dataots =[]
    #                            if tothour > myworkinghours:
    #                                myot = self.env['hr.overtime.list'].sudo().search([('workingday_id','=', myvalid.code.id)])
    #                                for allots in myot:
    #                                   if allots.ot_from and allots.ot_to:
    #                                        otfrom1 = str(allots.ot_from).split(':')[0]
    #                                        otfrom2 = str(allots.ot_from).split(':')[1]
    #                                        otfrom3 = str(allots.ot_from).split(':')[2]
    #                                        otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                        otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                        otto1 = str(allots.ot_to).split(':')[0]
    #                                        otto2 = str(allots.ot_to).split(':')[1]
    #                                        otto3 = str(allots.ot_to).split(':')[2]
    #                                        otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                        ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                        if timesouts >= otfroms:
    #                                            dataots.append({'timein': otfroms,
    #                                                            'timeout': ottos,
    #                                                            'mytimeout': timesouts,
    #                                                            'totalhour': timesouts - otfroms,
    #                                                            'othour': ottos - otfroms,
    #                                                            'ottipes': allots.ot_type})
    #                                if len(dataots) == 1:
    #                                    allentry.write({'ot1': dataots['ottipes'],
    #                                                   'ot1_time': dataots['totalhour'],
    #                                                    'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                                elif len(dataots) >1:
    #                                    cnt = 1
    #                                    for alldataots in dataots:
    #                                        if cnt ==1:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot1': alldataots['ottipes'],
    #                                                                'ot1_time': alldataots['timeout']- alldataots['timein']})
    #                                        elif cnt== 2:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': alldataots['timeout']- alldataots['timein']})
    #                                            else:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': timesouts - alldataots['timein']})
    #                                        else:
    #                                            allentry.write({'ot3': alldataots['ottipes'],
    #                                                            'ot3_time': timesouts - alldataots['timein']})
#
    #                                        cnt +=1
    #                                    allentry.write({'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                        elif hariaktifvalid == True and isholiday == False:
    #                            timein1 = str(allentry.time_in).split(':')[0]
    #                            timein2 = str(allentry.time_in).split(':')[1]
    #                            timein3 = str(allentry.time_in).split(':')[2]
    #                            timeins = time(int(timein1), int(timein2), int(timein3))
    #                            timeout1 = str(allentry.time_out).split(':')[0]
    #                            timeout2 = str(allentry.time_out).split(':')[1]
    #                            timeout3 = str(allentry.time_out).split(':')[2]
    #                            timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                            timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                            timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                            mytime = timesouts - timesins
    #                            # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                            tothour = 0
    #                            if str(mytime).find('day') != -1:
    #                                tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                            else:
    #                                tothour = int(str(mytime).split(':')[0])
    #                            fdfrom1 = str(myvalid.fullday_from).split(':')[0]
    #                            fdfrom2 = str(myvalid.fullday_from).split(':')[1]
    #                            fdfrom3 = str(myvalid.fullday_from).split(':')[2]
    #                            fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                            fdto1 = str(myvalid.fullday_to).split(':')[0]
    #                            fdto2 = str(myvalid.fullday_to).split(':')[1]
    #                            fdto3 = str(myvalid.fullday_to).split(':')[2]
    #                            fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                            fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                            fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                            myworkinghour = fullsdaysto - fullsdaysfrom
    #                            myworkinghours = 0
    #                            if str(myworkinghour).find('day') != -1:
    #                                myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                            else:
    #                                myworkinghours = int(str(myworkinghour).split(':')[0])
    #                            dataots =[]
    #                            if tothour > myworkinghours:
    #                                myot = self.env['hr.overtime.list'].sudo().search([('workingday_id','=', myvalid.code.id)])
    #                                for allots in myot:
    #                                   if allots.ot_from and allots.ot_to:
    #                                        otfrom1 = str(allots.ot_from).split(':')[0]
    #                                        otfrom2 = str(allots.ot_from).split(':')[1]
    #                                        otfrom3 = str(allots.ot_from).split(':')[2]
    #                                        otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                        otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                        otto1 = str(allots.ot_to).split(':')[0]
    #                                        otto2 = str(allots.ot_to).split(':')[1]
    #                                        otto3 = str(allots.ot_to).split(':')[2]
    #                                        otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                        ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                        if timesouts >= otfroms:
    #                                            dataots.append({'timein': otfroms,
    #                                                            'timeout': ottos,
    #                                                            'mytimeout': timesouts,
    #                                                            'totalhour': timesouts - otfroms,
    #                                                            'othour': ottos - otfroms,
    #                                                            'ottipes': allots.ot_type})
    #                                if len(dataots) == 1:
    #                                    allentry.write({'ot1': dataots['ottipes'],
    #                                                   'ot1_time': dataots['totalhour'],
    #                                                    'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                    })
#
    #                                elif len(dataots) >1:
    #                                    cnt = 1
    #                                    for alldataots in dataots:
    #                                        if cnt ==1:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot1': alldataots['ottipes'],
    #                                                                'ot1_time': alldataots['timeout']- alldataots['timein'],
    #                                                                'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                                })
    #                                        elif cnt== 2:
    #                                            if timesouts > alldataots['timeout']:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': alldataots['timeout']- alldataots['timein']})
    #                                            else:
    #                                                allentry.write({'ot2': alldataots['ottipes'],
    #                                                                'ot2_time': timesouts - alldataots['timein']})
    #                                        else:
    #                                            allentry.write({'ot3': alldataots['ottipes'],
    #                                                            'ot3_time': timesouts - alldataots['timein']})
#
    #                                        cnt +=1
#
    #                        else:
    #                            allentry.write({'ot1': 'Holiday'})
    #                            timein1 = str(allentry.time_in).split(':')[0]
    #                            timein2 = str(allentry.time_in).split(':')[1]
    #                            timein3 = str(allentry.time_in).split(':')[2]
    #                            timeins = time(int(timein1), int(timein2), int(timein3))
    #                            timeout1 = str(allentry.time_out).split(':')[0]
    #                            timeout2 = str(allentry.time_out).split(':')[1]
    #                            timeout3 = str(allentry.time_out).split(':')[2]
    #                            timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                            timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                            timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                            mytime = timesouts - timesins
    #                            tothour = 0
    #                            if str(mytime).find('day') != -1:
    #                                tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                            else:
    #                                tothour = str(mytime)
    #                            allentry.write({'ot1_time': tothour, 'tmsprocessing_id': alldata.id or alldata._origin.id})
#
    #                    else:
    #                        myholiday = self.env['resource.calendar.leaves'].sudo().search([('area_id','=',allentry.area_id.id),('branch_id','=',allentry.branch_id.id)])
    #                        isholiday = False
    #                        for allholi in myholiday:
    #                            datetime_from = datetime.strptime(str(allholi.date_from).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            datetime_to = datetime.strptime(str(allholi.date_to).split(' ')[0],
    #                                                             "%Y-%m-%d")
    #                            tglan = datetime.strptime(str(allentry.dates),
    #                                                             "%Y-%m-%d")
    #                            if tglan>= datetime_from and tglan <= datetime_to:
    #                                isholiday = True
    #                                break
    #                        myabsense = datetime.strptime(str(allentry.dates),'%Y-%m-%d')
    #                        hariabsen = myabsense.strftime('%A')
    #                        mywd = self.env['hr.working.days'].sudo().search([('area_id','=',allentry.area_id.id),('branch_id','=',allentry.branch_id.id)])
    #                        if mywd:
    #                            hariaktifvalid = False
    #                            if len(mywd) ==1:
    #                                hariaktifawal = mywd.working_day_from
    #                                hariaktifakhir = mywd.working_day_to
    #                                if not hariaktifawal or not hariaktifakhir:
    #                                    raise UserError ("There Is No Valid Working Days For Employee %s" %(allentry.employee_id.display_name))
    #                                myabsense = datetime.strptime(str(allentry.dates), '%Y-%m-%d')
    #                                hariabsen = myabsense.strftime('%A')
    #                                daytoint = False
    #                                if hariabsen == 'Sunday':
    #                                    daytoint = 0
    #                                elif hariabsen == 'Monday':
    #                                    daytoint = 1
    #                                elif hariabsen == 'Tuesday':
    #                                    daytoint = 2
    #                                elif hariabsen == ' Wednesday':
    #                                    daytoint = 3
    #                                elif hariabsen == 'Thursday':
    #                                    daytoint = 4
    #                                elif hariabsen == 'Friday':
    #                                    daytoint = 5
    #                                elif hariabsen == 'Saturday':
    #                                    daytoint = 6
    #                                if daytoint >= int(hariaktifawal) and daytoint <= int(hariaktifakhir):
    #                                    hariaktifvalid = True
    #                                if hariaktifvalid == True and isholiday == True:
    #                                    timein1 = str(allentry.time_in).split(':')[0]
    #                                    timein2 = str(allentry.time_in).split(':')[1]
    #                                    timein3 = str(allentry.time_in).split(':')[2]
    #                                    timeins = time(int(timein1), int(timein2), int(timein3))
    #                                    timeout1 = str(allentry.time_out).split(':')[0]
    #                                    timeout2 = str(allentry.time_out).split(':')[1]
    #                                    timeout3 = str(allentry.time_out).split(':')[2]
    #                                    timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                                    timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                                    timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                                    mytime = timesouts - timesins
    #                                    # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                                    tothour = 0
    #                                    if str(mytime).find('day') != -1:
    #                                        tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        tothour = int(str(mytime).split(':')[0])
    #                                    fdfrom1 = str(mywd.fullday_from).split(':')[0]
    #                                    fdfrom2 = str(mywd.fullday_from).split(':')[1]
    #                                    fdfrom3 = str(mywd.fullday_from).split(':')[2]
    #                                    fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                                    fdto1 = str(mywd.fullday_to).split(':')[0]
    #                                    fdto2 = str(mywd.fullday_to).split(':')[1]
    #                                    fdto3 = str(mywd.fullday_to).split(':')[2]
    #                                    fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                                    fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                                    fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                                    myworkinghour = fullsdaysto - fullsdaysfrom
    #                                    myworkinghours = 0
    #                                    if str(myworkinghour).find('day') != -1:
    #                                        myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        myworkinghours = int(str(myworkinghour).split(':')[0])
    #                                    dataots = []
    #                                    if tothour > myworkinghours:
    #                                        myot = self.env['hr.overtime.list'].sudo().search(
    #                                            [('workingday_id', '=', mywd.code.id)])
    #                                        for allots in myot:
    #                                            if allots.ot_from and allots.ot_to:
    #                                                otfrom1 = str(allots.ot_from).split(':')[0]
    #                                                otfrom2 = str(allots.ot_from).split(':')[1]
    #                                                otfrom3 = str(allots.ot_from).split(':')[2]
    #                                                otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                                otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                                otto1 = str(allots.ot_to).split(':')[0]
    #                                                otto2 = str(allots.ot_to).split(':')[1]
    #                                                otto3 = str(allots.ot_to).split(':')[2]
    #                                                otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                                ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                                if timesouts >= otfroms:
    #                                                    dataots.append({'timein': otfroms,
    #                                                                    'timeout': ottos,
    #                                                                    'mytimeout': timesouts,
    #                                                                    'totalhour': timesouts - otfroms,
    #                                                                    'othour': ottos - otfroms,
    #                                                                    'ottipes': allots.ot_type})
    #                                        if len(dataots) == 1:
    #                                            allentry.write({'ot1': dataots['ottipes'],
    #                                                            'ot1_time': dataots['totalhour'],
    #                                                            'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                            })
    #                                        elif len(dataots) > 1:
    #                                            cnt = 1
    #                                            for alldataots in dataots:
    #                                                if cnt == 1:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot1': alldataots['ottipes'],
    #                                                                        'ot1_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein'],
    #                                                                        'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                                                elif cnt == 2:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein'],
    #                                                                        'tmsprocessing_id': alldata.id or alldata._origin.id})
    #                                                    else:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': timesouts - alldataots[
    #                                                                            'timein']})
    #                                                else:
    #                                                    allentry.write({'ot3': alldataots['ottipes'],
    #                                                                    'ot3_time': timesouts - alldataots['timein']})
#
    #                                                cnt += 1
    #                                elif hariaktifvalid == True and isholiday == False:
    #                                    timein1 = str(allentry.time_in).split(':')[0]
    #                                    timein2 = str(allentry.time_in).split(':')[1]
    #                                    timein3 = str(allentry.time_in).split(':')[2]
    #                                    timeins = time(int(timein1), int(timein2), int(timein3))
    #                                    timeout1 = str(allentry.time_out).split(':')[0]
    #                                    timeout2 = str(allentry.time_out).split(':')[1]
    #                                    timeout3 = str(allentry.time_out).split(':')[2]
    #                                    timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                                    timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                                    timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                                    mytime = timesouts - timesins
    #                                    # mytimeouts = datetime.strptime(str(allentry.time_out).replace(" ", ''), '%H:%M:%S')
    #                                    tothour = 0
    #                                    if str(mytime).find('day') != -1:
    #                                        tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        tothour = int(str(mytime).split(':')[0])
    #                                    fdfrom1 = str(mywd.fullday_from).split(':')[0]
    #                                    fdfrom2 = str(mywd.fullday_from).split(':')[1]
    #                                    fdfrom3 = str(mywd.fullday_from).split(':')[2]
    #                                    fulldayfrom = time(int(fdfrom1), int(fdfrom2), int(fdfrom3))
    #                                    fdto1 = str(mywd.fullday_to).split(':')[0]
    #                                    fdto2 = str(mywd.fullday_to).split(':')[1]
    #                                    fdto3 = str(mywd.fullday_to).split(':')[2]
    #                                    fulldayto = time(int(fdto1), int(fdto2), int(fdto3))
    #                                    fullsdaysfrom = datetime.strptime(str(fulldayfrom), '%H:%M:%S')
    #                                    fullsdaysto = datetime.strptime(str(fulldayto), '%H:%M:%S')
    #                                    myworkinghour = fullsdaysto - fullsdaysfrom
    #                                    myworkinghours = 0
    #                                    if str(myworkinghour).find('day') != -1:
    #                                        myworkinghours = int(str(str(myworkinghour).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        myworkinghours = int(str(myworkinghour).split(':')[0])
    #                                    dataots = []
    #                                    if tothour > myworkinghours:
    #                                        myot = self.env['hr.overtime.list'].sudo().search(
    #                                            [('workingday_id', '=', mywd.id)])
    #                                        for allots in myot:
    #                                            if allots.ot_from and allots.ot_to:
    #                                                otfrom1 = str(allots.ot_from).split(':')[0]
    #                                                otfrom2 = str(allots.ot_from).split(':')[1]
    #                                                otfrom3 = str(allots.ot_from).split(':')[2]
    #                                                otfrom = time(int(otfrom1), int(otfrom2), int(otfrom3))
    #                                                otfroms = datetime.strptime(str(otfrom), '%H:%M:%S')
    #                                                otto1 = str(allots.ot_to).split(':')[0]
    #                                                otto2 = str(allots.ot_to).split(':')[1]
    #                                                otto3 = str(allots.ot_to).split(':')[2]
    #                                                otto4 = time(int(otto1), int(otto2), int(otto3))
    #                                                ottos = datetime.strptime(str(otto4), '%H:%M:%S')
    #                                                if timesouts >= otfroms:
    #                                                    dataots.append({'timein': otfroms,
    #                                                                    'timeout': ottos,
    #                                                                    'mytimeout': timesouts,
    #                                                                    'totalhour': timesouts - otfroms,
    #                                                                    'othour': ottos - otfroms,
    #                                                                    'ottipes': allots.ot_type})
    #                                        if len(dataots) == 1:
    #                                            allentry.write({'ot1': dataots['ottipes'],
    #                                                            'ot1_time': dataots['totalhour'],
    #                                                            'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                            })
    #                                        elif len(dataots) > 1:
    #                                            cnt = 1
    #                                            for alldataots in dataots:
    #                                                if cnt == 1:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot1': alldataots['ottipes'],
    #                                                                        'ot1_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein'],
    #                                                                        'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                                        })
    #                                                elif cnt == 2:
    #                                                    if timesouts > alldataots['timeout']:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': alldataots['timeout'] -
    #                                                                                    alldataots['timein']})
    #                                                    else:
    #                                                        allentry.write({'ot2': alldataots['ottipes'],
    #                                                                        'ot2_time': timesouts - alldataots[
    #                                                                            'timein']})
    #                                                else:
    #                                                    allentry.write({'ot3': alldataots['ottipes'],
    #                                                                    'ot3_time': timesouts - alldataots['timein']})
#
    #                                                cnt += 1
    #                                else:
    #                                    timein1 = str(allentry.time_in).split(':')[0]
    #                                    timein2 = str(allentry.time_in).split(':')[1]
    #                                    timein3 = str(allentry.time_in).split(':')[2]
    #                                    timeins = time(int(timein1), int(timein2), int(timein3))
    #                                    timeout1 = str(allentry.time_out).split(':')[0]
    #                                    timeout2 = str(allentry.time_out).split(':')[1]
    #                                    timeout3 = str(allentry.time_out).split(':')[2]
    #                                    timeouts = time(int(timeout1), int(timeout2), int(timeout3))
    #                                    timesins = datetime.strptime(str(timeins), '%H:%M:%S')
    #                                    timesouts = datetime.strptime(str(timeouts), '%H:%M:%S')
    #                                    mytime = timesouts - timesins
    #                                    tothour = 0
    #                                    if str(mytime).find('day') != -1:
    #                                        tothour = int(str(str(mytime).split(":")[0]).split(',')[1])
    #                                    else:
    #                                        tothour = str(mytime)
    #                                    allentry.write({'ot1': str('Holiday'),
    #                                                    'ot1_time': str(tothour),
    #                                                    'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                    })
#
    #                        else:
    #                            raise UserError("There is no Employee Groups Or Working Days Found for area = %s , bisnis_unit = %s and employee =%s !" %(allentry.area_id.name, allentry.branch_id.name, allentry.employee_id.display_name))
#
    #                else:
    #                    #if the tms entry not attendee then we search for the existing permition off the employee
    #                    mypermition = self.env['hr.permission.entry'].sudo().search([('employee_id','=',allentry.employee_id.id)])
    #                    haspermition = False
    #                    for allpermition in mypermition:
    #                        if allpermition.permission_date_from and allpermition.permission_date_To:
    #                            if allentry.dates >= allpermition.permission_date_from  and allentry.dates <= allpermition.permission_date_To:
    #                                haspermition = allpermition.id
#
    #                                break
    #                    if haspermition:
    #                        tmspermition = self.env['hr.permission.entry'].sudo().browse(haspermition)
    #                        #if exist the permition then set the flagg of attende to True for later used
    #                        isattende == True
    #                        if allentry.attendence_status == 'sick':
    #                            #if the attendence_status is sick check for working day or employee group
    #                            mygroup = self.env['hr.empgroup.details'].sudo().search(
    #                                [('department_id', '=', allentry.employee_id.department_id.id)])
    #                            myid = []
    #                            for allsgrps in mygroup:
    #                                myid.append(allsgrps.empgroup_id.id)
    #                            #search for employee has working day
    #                            myworkingday = self.env['hr.empgroup'].sudo().search([('id', 'in', myid)])
    #                            idwd = False
    #                            for allwd in myworkingday:
    #                                if allwd.valid_from and allwd.valid_to:
    #                                    #if there is valid working day that employee have beem setting up
    #                                    if allentry.dates >= allwd.valid_from and allentry.dates <= allwd.valid_to:
    #                                        idwd = allwd.id
    #                                        break
    #                            if tmspermition.permission_status =='approved2' or tmspermition.permission_status =='approved3':
    #                                #Found the working day for the employee
    #                                myworkingday = self.env['hr.empgroup'].browse(idwd)
    #                                #if the attendence_status in the tms entry =='sick' so we just set the tms entry time in and time out to the working day time in and time out
    #                                allentry.write({'time_in': myworkingday.fullday_from,
    #                                                'time_out': myworkingday.fullday_to,
    #                                                'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                })
    #                            else:
    #                                allentry.write({'time_in': '00:00:00',
    #                                                'time_out': '00:00:00',
    #                                                'attendence_status': 'absent',
    #                                                'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                                })
    #                        elif allentry.attendence_status == 'leave':
    #                            mygroup = self.env['hr.empgroup.details'].sudo().search(
    #                                [('department_id', '=', allentry.employee_id.department_id.id)])
    #                            myid = []
    #                            for allsgrps in mygroup:
    #                                myid.append(allsgrps.empgroup_id.id)
    #                            #search for employee has working day
    #                            myworkingday = self.env['hr.empgroup'].sudo().search([('id', 'in', myid)])
    #                            idwd = False
    #                            for allwd in myworkingday:
    #                                if allwd.valid_from and allwd.valid_to:
    #                                    #if there is valid working day that employee have beem setting up
    #                                    if allentry.dates >= allwd.valid_from and allentry.dates <= allwd.valid_to:
    #                                        idwd = allwd
    #                                        break
    #                            #Found the working day for the employee
    #                            myworkingday = self.env['hr.empgroup'].browse(idwd)
    #                            allentry.write({
    #                                            'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                            })
    #                    else:
    #                        allentry.write({'attendence_status':'absent',
    #                                        'time_in': '00:00:00',
    #                                        'time_out': '00:00:00',
    #                                        'tmsprocessing_id': alldata.id or alldata._origin.id
    #                                        })
#
#
    #    return True

    def action_view_tmsentry(self, tmsdetails=False):
        #View for tms entry
        if not tmsdetails:
            #if no data then search for data in tms sync with mapped data tmsentry_id
            tmsdetails = self.mapped('tmsentry_ids')
        #action will be given from sanbe_hr_tms.action_hr_tmsentry
        action = self.env['ir.actions.actions']._for_xml_id('sanbe_hr_tms.action_hr_tmsentry')
        if len(tmsdetails) > 1:
            #if data count in tms details greater than 1 then put the domain with the tmsdetailsids
            action['domain'] = [('id', 'in', tmsdetails.ids)]
        elif len(tmsdetails) == 1:
            #if data count in tms details is equal to 1 then open the form
            form_view = [(self.env.ref('sanbe_hr_tms.hr_tmsentry_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tmsdetails.id
        else:
            #else we closed it
            action = {'type': 'ir.actions.act_window_close'}
        #lets open the view eg tree with domain or form view
        return action
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
class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    tmsprocessing_id = fields.Many2one('hr.tms.processing',string='TMS Processing ID',index=True,tracking=True)
    tmspermission_id = fields.Many2one('hr.permission.entry',string='Tms Permition ID',index=True)