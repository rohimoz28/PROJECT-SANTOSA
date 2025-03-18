# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import pytz
from datetime import datetime,time, timedelta
import logging
_logger = logging.getLogger(__name__)
chari = {'0':6,'1':0,'2':1,'3':2,'4':3,'5':4,'6':5}
class HREmpGroupSetting(models.Model):
    _name = "hr.empgroup"
    _description = 'HR Employee Group Setting'
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    #Function For Filter Branch in Area
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area_id','branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id','=', allrecs.branch_id.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]
            
            allwds = self.env['hr.working.days'].sudo().search([('area_id','=',allrecs.area_id.id),('available_for','in',allrecs.branch_id.ids),('is_active','=',True)])
            #allrecs.wdcode_ids = [Command.set(allwds.ids)]
            
    # name = fields.Char('Code', copy=True,required=True)
    name = fields.Char(string='Code',default=lambda self: _('New'),
                       copy=False, readonly=True, tracking=True, requirement=True)
    description = fields.Char('Description', copy=True, tracking=True)
    #wdcode_ids = fields.Many2many('hr.working.days','wd_emp_rel',string='WD Code All', copy=True,compute='_isi_department_branch', store=False)
    #wdcode = fields.Many2one('hr.working.days',domain="[('id','in',wdcode_ids)]",string='WD Code', copy=True,index=True, required=True)
    area_id = fields.Many2one("res.territory", string='Area ID', copy=True, index=True, tracking=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_emp_rel', string='AllBranch', copy=True, compute='_isi_semua_branch', store=False, tracking=True)
    is_active = fields.Boolean('Active', copy=True,tracking=True)
    is_inactive = fields.Boolean('In Active', copy=True,tracking=True)
    islabelstate = fields.Char('Status', copy=True)
    branch_id = fields.Many2one('res.branch',string='Bisnis Unit', copy=True,index=True,domain="[('id','in',branch_ids)]",tracking=True)
    area_id = fields.Many2one("res.territory", string='Area ID', copy=True, index=True, required=True)
    alldepartment = fields.Many2many('hr.department','hr_department_emp_set_rel', string='All Department', copy=True,compute='_isi_department_branch',store=False, tracking=True)
    department_id = fields.Many2one('hr.department',domain="[('id','in',alldepartment)]", copy=True,string='Sub Department',tracking=True)
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('close','Close')], default='draft', copy=True, tracking=True)
    #valid_from = fields.Date('Valid From', required=True, copy=True)
    #valid_to = fields.Date('To', required=True, copy=True)
    summary_details_id = fields.Many2one('sb.tms.tmsentry.details', string='details')
    value_id = fields.Integer('value_id', compute='action_export_excel')
    value_name = fields.Char('value_name')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  ondelete='cascade', index=True)
    # employee_ids = fields.One2many('hr.employee', 'emp_group_id', string='employee')
    empgroup_ids = fields.One2many('hr.empgroup.details','empgroup_id',auto_join=True,string='Employee Group Setting Details', copy=True,tracking=True)
    # periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True)

    @api.depends('value_id')
    def _compute_value_id(self):
        for record in self:
            record.value_id = record.id
    
    @api.constrains('is_active', 'is_inactive')
    def _check_active(self):
        for rec in self:
            if rec.is_active == False:
                raise UserError('Must selected Active or In Active for this This Employee Group Setting')
            
    @api.onchange('is_active')
    def rubahactive(self):
        for rec in self:
            if rec.is_active == True:
                rec.is_inactive = False
            else:
                rec.is_inactive = True
            
    @api.onchange('is_inactive')
    def rubahactivex(self):
        for rec in self:
            if rec.is_inactive == True:
                rec.is_active = False
            else:
                rec.is_active = True
    
    def kumpulhari(self,wd1,wd2):
        listhr = []
        wda = wd1
        wdb = wd2
        while wda != wdb:
            listhr.append(chari[str(wda)])
            wda += 1
            if wda == 7 : wda = 0
        listhr.append(chari[str(wdb)])
        return listhr
        
    def cek_libur(self,tgl,area_id):
        sql = """
            select (date_from + interval '7 hours')::date, (date_to + interval '7 hours')::date 
            from resource_calendar_leaves
            where area_id={_area_id} and (date_from + interval '7 hours')::date <= '{_tgl}' 
                and (date_to + interval '7 hours')::date >= '{_tgl}'
            """.format(_area_id=area_id,_tgl=tgl)
            
        self._cr.execute(sql)
        hasil = self._cr.dictfetchall()
        return hasil
    
    def btn_approved(self):
        for rec in self:
            rec.state = 'approved'
    
    def btn_process(self):
        for res in self:
            for recx in res.empgroup_ids:
                #dtlookemp = self.env['hr.empgroup.details'].sudo().search([('employee_id','=',recx.employee_id.id),('periode_id','=',recx.periode_id.id),('state','!=','close')],order='valid_from asc')
                dtlookemp = self.env['hr.empgroup.details'].sudo().search([('employee_id','=',recx.employee_id.id),('state','!=','close')],order='valid_from asc')
                emp_list = []
                if dtlookemp:
                    for rec in dtlookemp:
                        if rec.wdcode:
                            wdffrom = int(rec.wdcode.working_day_from)
                            wdfto = int(rec.wdcode.working_day_to)
                            wdhffrom = int(rec.wdcode.working_half_from)
                            wdhfto = int(rec.wdcode.working_half_from)
                            is_off = False
                            
                            wd1 = None
                            wd2 = None
                            listhr = []
                            listhr_half = []
                            wd1 = wdffrom
                            wd2 = wdfto
                            listhr = self.kumpulhari(wd1,wd2)
                                    
                            if rec.wdcode.type_hari == 'fhday':
                                wd1 = wdhffrom
                                wd2 = wdhfto
                                listhr_half = self.kumpulhari(wd1,wd2)
                                
                            #tmsentry = self.env['hr.attendance'].sudo().search([('periode_id','=',recx.periode_id.id),('employee_id','=',rec.employee_id.id),('dates','>=',rec.valid_from),('dates','<=',rec.valid_to),('area_id', '=', rec.area_id.id),('branch_id', '=', rec.branch_id.id)],order='employee_id asc, dates asc')
                            #tmsentry = self.env['hr.attendance'].sudo().search([('employee_id','=',rec.employee_id.id),('dates','>=',rec.valid_from),('dates','<=',rec.valid_to),('area_id', '=', rec.area_id.id),('branch_id', '=', rec.branch_id.id)],order='employee_id asc, dates asc')
                            tmsentry = self.env['hr.attendance'].sudo().search([('employee_id','=',rec.employee_id.id),('area_id', '=', rec.area_id.id),('branch_id', '=', rec.branch_id.id)],order='employee_id asc, dates asc')
                            for rex in tmsentry:
                                if rex.dates >=rec.valid_from and rex.dates<=rec.valid_to:
                                    emp_list.append(rex.id)
                                    #day_of_week = (rex.dates.weekday() + 1) % 7
                                    day_of_week = rex.dates.weekday()
                                    chol = []
                                    dy = ''
                                    
                                    if listhr or listhr_half:
                                        #if day_of_week >= wd1 and day_of_week <= wd2:
                                        if day_of_week in listhr or day_of_week in listhr_half:
                                            chol = self.cek_libur(rex.dates,rex.area_id.id)
                                            if chol:
                                                dy = 'h'
                                            else:
                                                dy = 'w'
                                            is_off = False
                                        else:
                                            dy = 'h'
                                            is_off = True
                                            
                                            
                                        att_stat = False
                                        if (rex.time_in and rex.time_out) or \
                                            (rex.time_in_edited and rex.time_out) or \
                                            (rex.time_in and rex.time_out_edited) or \
                                            (rex.time_in_edited and rex.time_out_edited):
                                            att_stat = 'attendee'
                                        else:
                                            if dy == 'w':
                                                att_stat = 'absent'
                                        
                                        if rec.wdcode.type_hari == 'fday' or rec.wdcode.type_hari == 'fhday' or rec.wdcode.type_hari == 'hday':
                                            rex.sudo().write({
                                                'wdcode':rec.wdcode.id,
                                                'day_type':dy,
                                                'codes':self.id if (is_off == False) else False,
                                                'valid_from':rec.valid_from if (is_off == False) else False,
                                                'valid_to':rec.valid_to if (is_off == False) else False,
                                                'attendence_status':att_stat if is_off == False else False,
                                            })
                                else:
                                    chol = self.cek_libur(rex.dates,rex.area_id.id)
                                    if chol:
                                        dy = 'h'
                                    else:
                                        dy = 'w'
                                    rex.sudo().write({
                                        'wdcode': False,
                                        'day_type':dy,
                                        'codes':False,
                                        'valid_from':False,
                                        'valid_to':False,
                                        'attendence_status':False,
                                        'time_in':False,
                                        'time_out':False,
                                        'time_in_edited':False,
                                        'time_out_edited':False,
                                        'tgl_masuk':False,
                                        'tgl_keluar':False,
                                        
                                        'ot1' : False,
                                        'ot1_time' : False,
                                        'ot2' : False,
                                        'ot2_time' : False,
                                        'ot3' : False,
                                        'ot3_time' : False,
                                        'ot4' : False,
                                        'ot4_time' : False,
                                        'ot_auto' : False,
                                        'ot_auto_time' : False,
                                        'att_time' : False,
                                        'add_hour' : False,
                                        'night_shift' : False,
                                        'delayed' : False,
                                        'premi_attendee' : False,
                                        'tunjangan_trp' : False,
                                        'ot1_timex' : False,
                                        'ot2_timex' : False,
                                        'ot3_timex' : False,
                                        'ot4_timex' : False,
                                        'ot_auto_timex' : False,
                                        'wd_type' : False,
                                        'hour_adv' : False,
                                        'permision_code' : False,
                                        'tunjagan_meal' : False,
                                        'plan_ot_from' : False,
                                        'plan_ot_to' : False,
                                        'approval_ot_from' : False,
                                        'approval_ot_to' : False
                                    })
                                        
                                    #elif rec.wdcode.type_hari == 'hday':
                                    #    if dy == 'h':
                                    #        rex.sudo().write({
                                    #            'wdcode':rec.wdcode.id,
                                    #            'day_type':dy,
                                    #            'codes':self.id,
                                    #            'valid_from':rec.valid_from,
                                    #            'valid_to':rec.valid_to,
                                    #            'attendence_status':att_stat,
                                    #        })
                    #if emp_list:
                    #    #updtms = self.env['hr.attendance'].sudo().search([('periode_id','=',recx.periode_id.id),('employee_id','=',recx.employee_id.id),('id','not in',emp_list)])
                    #    updtms = self.env['hr.attendance'].sudo().search([('employee_id','=',recx.employee_id.id),('id','not in',emp_list)])
                    #    if updtms:
                    #        print('99999999999999999999')
                    #        print(updtms)
                    #        print('99999999999999999999')
                    #        for sisa in updtms:
                    #            sisa.sudo().write({
                    #                'wdcode':False,
                    #                'day_type':False,
                    #                'codes':False,
                    #                'valid_from':False,
                    #                'valid_to':False,
                    #                'attendence_status':False,
                    #            })
                    
    def btn_close(self):
        for rec in self:
            rec.state = 'close'
    
    def btn_draft(self):
        for rec in self:
            rec.state = 'draft'
    
    def btn_clear_child(self):
        for rec in self:
            if rec.empgroup_ids:
                rec.empgroup_ids.unlink()
            
    #Function For PopUp Search Employee
    def action_search_employee(self):
            #if self.department_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Search Employee'),
                'res_model': 'hr.employeedepartment',
                'view_mode': 'form',
                'target': 'new',
                'limit': 1000,  # Limit to the first 100 records
                'domain': [('department_id', '=', self.department_id.id)],
                'context': {
                    'active_id': self.id,
                    'default_modelname':'hr.empgroup',
                    'default_area_id':self.area_id.id,
                    'default_branch_id':self.branch_id.id,
                    'default_department_id':self.department_id.id,
                    #'default_periode_id':self.periode_id.id,
                    #'default_valid_from':self.valid_from,
                    #'default_valid_to':self.valid_to
                    },
                'views': [[False, 'form']]
            }
            #else:
            #    raise UserError('Sub Department Not Selected')

    def action_generate_employee_group(self):
        try:
            self.env.cr.execute("CALL generate_empgroup()")
            self.env.cr.commit()
            _logger.info("Stored procedure executed successfully.")
        except Exception as e:
            _logger.error("Error calling stored procedure: %s", str(e))
            raise UserError("Error executing the function: %s" % str(e))

    def action_export_excel(self, model_id=None):
        self.ensure_one()
        # value_id = self.value_id
        tms_summary_domain = []
        if self.area_id:
            tms_summary_domain.append(('area', '=', self.area_id.id))
        if self.branch_id:
            tms_summary_domain.append(('branch_id', '=', self.branch_id.id))
        if self.department_id:
            tms_summary_domain.append(('department_id', '=', self.department_id.id))
        
        tms_summaries = self.env['hr.employee'].search(tms_summary_domain)
        _logger.info(f"Domain: {tms_summary_domain}")
        _logger.info(f"TMS Summaries: {tms_summaries}")
        
        # _logger.info(f"ID: {value_id}")
        value = self.env['value.group'].create({
                'value_id': self.id,
                'value_name': self.name
            })
                    
        if not tms_summaries:
            raise UserError(_("Tidak Ada Datas Record Dari data yang dipilih"))

        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.rekap_empgroup_xls',
            'report_type': 'xlsx',
            'report_file': f'Rekap_Empgroup_{self.department_id.name or "All"}',
            'context': {
                'active_model': 'hr.tmsentry.summary',
                'active_ids': tms_summaries.ids,
            }
        }
        

    # restart running number
    def _reset_sequence_empgroup(self):
        sequences = self.env['ir.sequence'].search([('code', '=like', '%hr.empgroup%')])
        sequences.write({'number_next_actual': 1})
        print(">>>>>>>>>>>>>>>")
        print("sequences:",sequences)
        print(">>>>>>>>>>>>>>>")

    #Function For AutoFill data Employee Based On Code
    @api.onchange('code')
    def _isi_details(self):
        for allrec  in self:
            if not allrec.code:
                return
            allrec.area_id = allrec.code.area_id.id
            allrec.branch_id = allrec.code.branch_id.id
            allrec.working_day_from = allrec.code.working_day_from
            allrec.working_day_to = allrec.code.working_day_to
            allrec.isbasic_wd = allrec.code.isbasic_wd
            allrec.fullday_from = allrec.code.fullday_from
            allrec.fullday_to = allrec.code.fullday_to
            allrec.halfday_from = allrec.code.halfday_from
            allrec.halfday_to = allrec.code.halfday_to

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                if 'area_id' in vals:
                    area = vals.get('area_id')
                    department = vals.get('department_id')
                    branch_id = vals.get('branch_id')
                    dt_area = self.env['res.territory'].sudo().search([('id','=',int(area))],limit=1)
                    dept = self.env['hr.department'].sudo().search([('id','=',int(department))],limit=1)
                    department_code = dept.department_code
                    branch = self.env['res.branch'].sudo().search([('id','=',int(branch_id))],limit=1)
                    branch_unit_id = branch.unit_id
                    if dt_area:
                        tgl = fields.Date.today()
                        tahun = str(tgl.year)[2:]
                        bulan = str(tgl.month)
                        # vals['name'] = cdo + str(tahun) + str(self.env['ir.sequence'].next_by_code('hr.overtime.planning'))
                        vals['name'] = f"{tahun}/{bulan}/{branch_unit_id}/EG/{department_code}/{self.env['ir.sequence'].next_by_code('hr.empgroup')}"
                        print(">>>>>>>>>>>>")
                        print("sequence:",vals['name'])
                        print(">>>>>>>>>>>>")
        res = super(HREmpGroupSetting,self).create(vals_list)
        return res


  
class ValueGroup(models.TransientModel):
    _name = 'value.group'
    _description = 'Value Group'

    value_id = fields.Integer('value_id')
    value_name = fields.Char('value_name')
    

#Details Data 
class HREmpGroupSettingDetails(models.Model):
    _name = "hr.empgroup.details"
    _description = 'HR Employee Group Setting Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area_id','branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id','=', allrecs.branch_id.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]
            
            allwds = self.env['hr.working.days'].sudo().search([('area_id','=',allrecs.area_id.id),('available_for','in',allrecs.branch_id.ids),('is_active','=',True)])
            allrecs.wdcode_ids = [Command.set(allwds.ids)]

    empgroup_id = fields.Many2one('hr.empgroup',string='Employee Group Setting ID', index=True,tracking=True)
    empgroup_name = fields.Char(string='Empgroup Name', required=False,tracking=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_emp_detail_rel', string='AllBranch', copy=True, compute='_isi_semua_branch', store=False,tracking=True)
    branch_id = fields.Many2one('res.branch',string='Bisnis Unit', copy=True,index=True,domain="[('id','in',branch_ids)]",tracking=True)
    area_id = fields.Many2one("res.territory", string='Area ID', copy=True, index=True,tracking=True)
    alldepartment = fields.Many2many('hr.department','hr_department_emp_detail_set_rel', string='All Department', copy=True,compute='_isi_department_branch',store=False,tracking=True)
    department_id = fields.Many2one('hr.department',string='Sub Department',copy=True,index=True,domain="[('id','in',alldepartment)]",tracking=True)
    wdcode_ids = fields.Many2many('hr.working.days','wd_emp_detail_rel',string='WD Code All', copy=True,compute='_isi_department_branch', store=False,tracking=True)
    wdcode = fields.Many2one('hr.working.days',domain="[('id','in',wdcode_ids)]",string='WD Code', copy=True,index=True,tracking=True)
    wdcode_name = fields.Char(string='WD Code Name', required=False,tracking=True)
    employee_id = fields.Many2one('hr.employee',string='Employee Name',index=True,domain="[('area','=',area_id),('branch_id','=',branch_id),('department_id','=',department_id),('state','=','approved')]",tracking=True)
    nik = fields.Char('NIK',tracking=True)
    job_id = fields.Many2one('hr.job',string='Job Position',index=True,tracking=True)
    valid_from = fields.Date('Valid From', required=True, copy=True,tracking=True)
    valid_to = fields.Date('To', required=True, copy=True,tracking=True)
    emp_status = fields.Selection([('probation','Probation'),
                                   ('confirmed','Confirmed'),
                                   ('probation', 'Probation'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('terminated', 'Terminated'),
                                   ],string='Employment Status',related='employee_id.emp_status',store=False,tracking=True)
    #periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True)
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('close','Close')], string='State',related='empgroup_id.state',store=True,tracking=True)

    def _message_log(self, body='', subject=False, message_type='notification', **kwargs):
        print(body, subject, message_type, kwargs)
        body = "Employee Name: %s, WD Code: %s %s" %(self.employee_id.name, self.wdcode.code, body)
        self.empgroup_id._message_log(body=body, subject=subject, message_type=message_type, **kwargs)

    #Function For Autofill Employee data based on Employee_id
    def btn_clear(self):
        raise UserError(self.empgroup_id)
    
    @api.model_create_multi
    def create(self, values):
        for vals in values:
            if 'valid_from' in vals and 'valid_to' in vals and 'employee_id' in vals:
                tfrom = (datetime.strptime(str(vals['valid_from']), "%Y-%m-%d").date())
                tto = (datetime.strptime(str(vals['valid_to']), "%Y-%m-%d").date())
                demp = self.env['hr.empgroup.details'].sudo().search([('empgroup_id','!=',False),('employee_id','=',int(vals['employee_id'])),('valid_from','<=',tfrom),('valid_to','>=',tfrom)])
                empgroup_name = demp.empgroup_id.name if demp.empgroup_id else "Unknown Group"
                if demp:
                    raise UserError(f'Valid From overlaps with existing data in EMP Group: {empgroup_name}')
                demp = self.env['hr.empgroup.details'].sudo().search([('empgroup_id','!=',False),('employee_id','=',int(vals['employee_id'])),('valid_from','<=',tto),('valid_to','>=',tto)])
                if demp:
                    raise UserError(f'Valid to over with existing data in EMP Group: {empgroup_name}')
        res = super(HREmpGroupSettingDetails,self).create(values)
        return res
    
    @api.constrains('employee_id','valid_from','valid_to')
    def cek_tgl(self):
        for rec in self:
            tfrom = (datetime.strptime(str(rec.valid_from), "%Y-%m-%d").date())
            tto = (datetime.strptime(str(rec.valid_to), "%Y-%m-%d").date())
            if rec.valid_from > rec.valid_to:
                raise UserError('Date Valid To must be bigger then Date Valid From')
            datecek = self.env['hr.empgroup.details'].sudo().search([('empgroup_id','!=',False),('id','!=',rec.id),('employee_id','=',rec.employee_id.id),('valid_from','<=',tfrom),('valid_to','>=',tfrom)])
            if datecek:
                raise UserError('Valid From over lap with existing data')
            datecek = self.env['hr.empgroup.details'].sudo().search([('empgroup_id','!=',False),('id','!=',rec.id),('employee_id','=',rec.employee_id.id),('valid_from','<=',tto),('valid_to','>=',tto)])
            
            if datecek:
                raise UserError('Valid to over lap with existing data')
    
    @api.onchange('employee_id')
    def isi_employee(self):
        for allrec in self:
            if not allrec.employee_id:
                return
            allrec.nik = allrec.employee_id.nik
            allrec.department_id = allrec.employee_id.department_id.id
            allrec.job_id = allrec.employee_id.job_id.id


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
        return (arch, view)