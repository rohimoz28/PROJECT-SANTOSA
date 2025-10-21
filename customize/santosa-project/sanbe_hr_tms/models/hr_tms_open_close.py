# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
# from Demos.FileSecurityTest import permissions
import pdb

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
import pytz
from datetime import timedelta, datetime, time,date
import dateutil.parser
import holidays
from datetime import datetime
date_format = "%Y-%m-%d"
from odoo.exceptions import AccessError, MissingError, UserError,RedirectWarning
import requests
import logging

_logger = logging.getLogger(__name__)

chari = {'0':6,'1':0,'2':1,'3':2,'4':3,'5':4,'6':5}

class HRTmsOpenClose(models.Model):
    _name = "hr.opening.closing"
    _description = 'HR TMS Open And Close'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id DESC'

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids=[Command.set(allbranch.ids)]

    # @api.depends('branch_id')
    # def _isi_semua_branch(self):
    #     for record in self:
    #         resbranch = self.env['res.branch'].sudo().search([])
    #         branch = resbranch.filtered(lambda p: p.id == record.branch_id)
    #         record.branch_ids = branch.id

    name = fields.Char('Period Name')
    area_id = fields.Many2one('res.territory',string='Area', index=True,store=True )
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    branch_id = fields.Many2one('res.branch',string='Business Unit',index=True,domain="[('id','in',branch_ids)]",store=True)
    open_periode_from = fields.Date('Opening Periode From',store=True)
    open_periode_to = fields.Date('Opening Periode To',store=True)
    close_periode_from = fields.Date('Closing Periode From')
    close_periode_to = fields.Date('Closing Periode To')
    isopen = fields.Boolean('Is Open',default=False)
    state_process = fields.Selection(
        [
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Close'),
            ('transfer_to_payroll', 'Transfer To Payroll')
        ],
        default='draft',
        String='Process State',
        tracking=True)

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
    
    @api.model_create_multi
    def create(self, values):
        for vals in values:
            if ('branch_id' in vals) and ('open_periode_from' in vals):
                
                open_periode_to = datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d")
                today = datetime.today()

                current_month = today.month
                current_year = today.year

                next_month = current_month + 1 if current_month < 12 else 1
                next_month_year = current_year if current_month < 12 else current_year + 1

                # Cek apakah bulan dan tahun dari open_periode_to sesuai
                if not ((open_periode_to.month == current_month and open_periode_to.year == current_year) or
                        (open_periode_to.month == next_month and open_periode_to.year == next_month_year)):
                    raise UserError(_('Tanggal "Open Periode To" hanya boleh di bulan ini atau bulan depan.'))
                
                
                br = self.env['res.branch'].sudo().search([('id', '=', vals['branch_id'])])
                date_obj = datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d")
                vals['name'] = date_obj.strftime("%B %Y") + ' | ' + br['name']

                check1 = self.env['hr.tmsentry.summary'].sudo().search([
                    ('branch_id', '=', br.id),
                    ('date_from', '<=', datetime.strptime(str(vals['open_periode_from']), "%Y-%m-%d").date()),
                    ('date_to', '>=', datetime.strptime(str(vals['open_periode_from']), "%Y-%m-%d").date())
                ])
                if check1:
                    raise UserError('Open Periode From for This Branch Already Used')

                check2 = self.env['hr.tmsentry.summary'].sudo().search([
                    ('branch_id', '=', br.id),
                    ('date_from', '<=', datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d").date()),
                    ('date_to', '>=', datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d").date())
                ])
                if check2:
                    raise UserError('A record with the same branch and running state already exsist')
            else:
                raise UserError('Branch or Open Periode From Not Selected')# --- Cek Periode Running (Logic Wizard) ---
            existing_record = self.env['hr.opening.closing'].sudo().search([
                ('area_id', '=', vals.get('area_id')), 
                ('branch_id', '=', vals['branch_id']), 
                ('state_process', '=', 'running')
            ], limit=1)
            
            if existing_record:
                existing_draft_record = self.env['hr.opening.closing'].sudo().search([
                    ('area_id', '=', vals.get('area_id')), 
                    ('branch_id', '=', vals['branch_id']), 
                    ('state_process', '=', 'draft')
                ])
                if len(existing_draft_record)>=1:
                    raise UserError(_('Allowed just 1 Running and 1 Draft Periode'))
            res =  super(HRTmsOpenClose, self).create(vals)
            return res

    #def init(self):
    #    dat = self.env['hr.opening.closing'].sudo().search([])
    #    for rec in dat:
    #        if rec.branch_id and rec.open_periode_from and rec.open_periode_to:
    #            br = self.env['res.branch'].sudo().search([('id','=',rec.branch_id.id)])
    #            #rec.name = br.name + '/' +str(datetime.strptime(str(rec.open_periode_from), "%d-%m-%Y").date())+'-'+str(datetime.strptime(str(rec.open_periode_to), "%d-%m-%Y").date())
    #            if br:
    #                rec.write({'name': br.name + '/' + str((datetime.strptime(str(rec.open_periode_from), "%Y-%m-%d").date()).strftime('%d-%m-%Y'))+'-'+str((datetime.strptime(str(rec.open_periode_to), "%Y-%m-%d").date()).strftime('%d-%m-%Y'))})
    #                rec.env.cr.commit()

    def write(self, vals):
        for rec in self:
            if rec.branch_id and rec.open_periode_from and rec.open_periode_to:
                open_close_data = self.env['hr.opening.closing'].sudo().search([('id', '=', rec.id)])
                br = self.env['res.branch'].sudo().search([('id', '=', rec.branch_id.id)])

                # Convert date object to string before strptime
                date_string = open_close_data.open_periode_to.strftime("%Y-%m-%d")
                date_obj = datetime.strptime(date_string, "%Y-%m-%d")
                vals['name'] = date_obj.strftime("%B %Y") + ' | ' + br['name']
        res = super(HRTmsOpenClose, self).write(vals)
        return res

    def compute_concate(self):
        print("MULAI CONCATE")
        recompute_tms = self.env['hr.tmsentry.summary'].sudo().search([])
        for record in recompute_tms:
            print(record.periode_id.name + str(record.date_from) + str(record.date_to), "ini yang baru")
            record.periode_from_to = record.periode_id.name + " | " + str(record.date_from) + " | " + str(record.date_to)

    def action_reproses(self):
        for data in self:
            period_id = data.id
            area_id = data.area_id
            branch_id = data.branch_id

            body = _('Re-Process Period')
            data.message_post(body=body)

            if data.state_process == 'done':
                raise UserError("Sudah Close")

            try:
                self.env.cr.execute("CALL calculate_tms(%s, %s, %s)", (period_id, area_id.id, branch_id.id))
                self.env.cr.commit()
                self.recompute_tms_summary()
                _logger.info("Stored procedure executed successfully for period_id: %s", period_id)
            except Exception as e:
                _logger.error("Error calling stored procedure: %s", str(e))
                raise UserError("Error executing the function: %s" % str(e))

            data.isopen = True
            data.state_process = "running"
        
        self.compute_concate()

    def recompute_tms_summary(self):
        for rec in self:
            tms_summary_data = self.env['hr.tmsentry.summary'].sudo().search([
                ('periode_id', '=', rec.id),
                ('area_id', '=', rec.area_id.id),
                ('branch_id', '=', rec.branch_id.id)
            ])

            employee_ids = tms_summary_data.mapped('employee_id.id')

            hr_employee_data = self.env['hr.employee'].sudo().search([
                ('id', 'in', employee_ids)
            ])

            employee_dict = {emp.id: emp for emp in hr_employee_data}
            
            for tsd in tms_summary_data:
                employee = employee_dict.get(tsd.employee_id.id)
                if employee:
                    tsd.ot = employee.allowance_ot
                    tsd.ot_flat = employee.allowance_ot_flat
                    tsd.night_shift = employee.allowance_night_shift

    def action_opening_periode(self):
        for data in self:
            if not data.open_periode_from or not data.open_periode_to:
                raise UserError(
                    "The 'Periode From' and 'Periode To' fields are required. Please enter values for both fields."
                )

            period_id = data.id
            area_id = data.area_id
            branch_id = data.branch_id

            body = _('Process Period: %s' % self.state_process)
            data.message_post(body=body)

            ''' validasi : Seluruh employee group yg sesuai area & branch nya sama dengan
            area & branch dari proses open period yg sedang dijalankan,
            harus sudah berstatus approve '''
            employee_group = self.env['hr.empgroup'].sudo().search([
                ('area_id', '=', area_id.id),
                ('branch_id', '=', branch_id.id),
                ('state', '!=', 'approved')
            ])

            if len(employee_group) > 1:
                raise UserError('Ensure all employee groups have been approved.')

            existing_record = self.search([('branch_id', '=', branch_id.id), ('state_process', '=', 'running'),('id','!=',data.id)])
            if existing_record:
                raise UserError('A record with the same branch and running state already exists.')

            # try:
            #     self.env.cr.execute("CALL calculate_tms(%s, %s, %s)", (period_id, area_id.id, branch_id.id))
            #     self.env.cr.commit()
            #     _logger.info("Stored procedure executed successfully for period_id: %s", period_id)
            # except Exception as e:
            #     _logger.error("Error calling stored procedure: %s", str(e))
            #     raise UserError("Error executing the function: %s" % str(e))

            data.isopen = True
            data.state_process = "running"

    def action_closing_periode(self):
        for data in self:
            
            # permintaan dari pa Gilang untuk menonaktifkan validasi dan proses closing kecuali update status
            # karena prosesnya disamakan dengan proses yang ada di ERP sanbe (27 Sept 2025)
            
            # summary = self.env['hr.tmsentry.summary'].search([('periode_id','=',data.id)])
            # # import pdb
            # # pdb.set_trace()
            # for record in summary:
            #     record.write({'state': 'done'})
            #     attendances = self.env['sb.tms.tmsentry.details'].search([('tmsentry_id','=',record.id)])
            #     for attn in attendances:
            #         attn.write({'status': 'done'})
            #     permissions = self.env['hr.permission.entry'].search([('periode_id','=',record.periode_id.id)])
            #     for perm in permissions:
            #         # perm.write({'permission_status': 'done'})
            #         perm.write({'permission_status': 'close'})
            #     overtime = self.env['hr.overtime.planning'].search([('periode_id','=',data.id)])
            #     for ot in overtime:
            #         ot.write({'state': 'done'})

            data.write({'state_process': 'done', 'isopen': 'false'})
            data.write({'isopen': 0})

            # search_permission = self.env['hr.permission.entry'].sudo().search([
            #     ('permission_date_from', '>=', data.open_periode_from),
            #     ('permission_date_To', '<=', data.open_periode_to),
            #     ('branch_id', '=', data.branch_id.id),
            #     ('area_id', '=', data.area_id.id),
            #     ('permission_status', '=', 'approved')
            # ])
            #
            # # Update status di permission entry = close (done)
            # search_permission.write({'permission_status': 'done'})

    def transfer_payroll(self):
        pass
        
        # for data in self:
        #     searchpermission = self.env['hr.permission.entry'].sudo().search([
        #         ('permission_date_from', '>=', data.open_periode_from),
        #         ('permission_date_To', '<=', data.open_periode_to),
        #         ('branch_id', '=', data.branch_id.id),
        #         ('area_id', '=', data.area_id.id)
        #     ])

        #     for permission in searchpermission:
        #         permission.permission_status = 'done'

        # for alldata in self:
        #     # if not alldata.close_periode_from or not alldata.close_periode_to:
        #     #     raise UserError("Please Input Periode From And To First")
        #     carisummary = self.env['hr.tmsentry.summary'].sudo().search([
        #         ('date_from', '=', alldata.open_periode_from),
        #         ('date_to', '<=', alldata.open_periode_to),
        #         ('branch_id', '=', alldata.branch_id.id)
        #     ])
        #     for allsummary in carisummary:
        #         if allsummary.state != 'transfer_payroll':
        #             raise UserError('The Closing process cannot be carried out because there still transaction that have not been transffered to payroll')
        #         else:
        #             allsummary.write({'state': 'done'})
        #     return

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name','in',['User TMS','HRD CA'])])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
                for node in arch.xpath("//tree"):
                    node.set('create', '0')
                for node in arch.xpath("//form"):
                    node.set('create', '0')
        return arch, view