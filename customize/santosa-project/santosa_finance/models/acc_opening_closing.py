# -*- coding: utf-8 -*-
import pdb

from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError
import pytz
from datetime import timedelta, datetime, time,date
import dateutil.parser
import holidays
from datetime import datetime
import requests
import logging

_logger = logging.getLogger(__name__)

date_format = "%Y-%m-%d"
chari = {'0':6,'1':0,'2':1,'3':2,'4':3,'5':4,'6':5}


class AccOpeningClosing(models.Model):
    _name = 'acc.periode.closing'
    _description = 'Accounting Period Setting'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
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
    area_id = fields.Many2one('res.territory',string='Area', index=True )
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    branch_id = fields.Many2one('res.branch',string='Business Unit', required=True, index=True, domain="[('id','in',branch_ids)]")
    open_periode_from = fields.Date('Opening Periode From')
    open_periode_to = fields.Date('Opening Periode To')
    close_periode_from = fields.Date('Closing Periode From')
    close_periode_to = fields.Date('Closing Periode To')
    
    def unlink(self):
        if self.state_process!='draft':
            raise UserError('Cannot Delete Account Closing Periode with state not in DRAFT')
        else:
            return super(AccOpeningClosing, self).unlink()
    
    @api.constrains('open_periode_from','open_periode_to')
    def _check_validation_training(self):
        for record in self:
            if record.open_periode_from > record.open_periode_to :
                raise UserError("harap masukan Masa Periode yang benar")
            
    isopen = fields.Boolean('Is Open',default=False)
    state_process = fields.Selection(
        [
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Close')
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
                if 'open_periode_from' in vals:
                    br = self.env['res.branch'].sudo().search([('id', '=', vals['branch_id'])])
                    date_obj = datetime.strptime(vals['open_periode_to'], "%Y-%m-%d")
                    vals['name'] = date_obj.strftime("%B %Y") + ' | ' + br['name']
        #            check = self.env['hr.tmsentry.summary'].sudo().search([
        #                 ('branch_id', '=', br.id),
        #                 ('date_from', '<=', datetime.strptime(str(vals['open_periode_from']),"%Y-%m-%d").date()),
        #                 ('date_to', '>=', datetime.strptime(str(vals['open_periode_from']), "%Y-%m-%d").date())
        #             ])
        #             if check:
        #                 raise UserError('Open Periode From for This Branch Already Used')
        #             check = self.env['hr.tmsentry.summary'].sudo().search([
        #                 ('branch_id', '=', br.id),
        #                 ('date_from', '<=', datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d").date()),
        #                 ('date_to', '>=', datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d").date())])
        #             if check:
        #                 raise UserError('Tanggal period ini sudah di gunakan')
        #     else:
        #         raise UserError('Branch or Open Periode From Not Selected')

            existing_record = self.search([('branch_id', '=', vals['branch_id']), ('state_process', '=', 'running')])
            if existing_record:
                raise UserError(_("A record with the same branch and running state already exists."))
        res = super(AccOpeningClosing, self).create(values)
        return res

    def init(self):
       dat = self.env['acc.periode.closing'].sudo().search([])
       for rec in dat:
    #        pass
           if rec.branch_id and rec.open_periode_from and rec.open_periode_to:
               br = self.env['res.branch'].sudo().search([('id','=',rec.branch_id.id)])
               rec.name = br.name + '/' +str(datetime.strptime(str(rec.open_periode_from), "%Y-%m-%d").date())+'-'+str(datetime.strptime(str(rec.open_periode_to), "%Y-%m-%d").date())
               if br:
                   rec.write({'name': br.name + '/' + str((datetime.strptime(str(rec.open_periode_from), "%Y-%m-%d").date()).strftime('%Y-%m-%d'))+'-'+str((datetime.strptime(str(rec.open_periode_to), "%Y-%m-%d").date()).strftime('%Y-%m-%d'))})
                   rec.env.cr.commit()

    def write(self, vals):
        for rec in self:
        #     pass
            if rec.branch_id and rec.open_periode_from and rec.open_periode_to:
                open_close_data = self.env['acc.periode.closing'].sudo().search([('id', '=', rec.id)])
                br = self.env['res.branch'].sudo().search([('id', '=', rec.branch_id.id)])

        #         # Convert date object to string before strptime
                date_string = open_close_data.open_periode_to.strftime("%Y-%m-%d")
                date_obj = datetime.strptime(date_string, "%Y-%m-%d")
                vals['name'] = date_obj.strftime("%B %Y") + ' | ' + br['name']
        res = super(AccOpeningClosing, self).write(vals)
        return res

    def compute_concate(self):
        print("MULAI CONCATE")
        # recompute_tms = self.env['hr.tmsentry.summary'].sudo().search([])
        # for record in recompute_tms:
        #     print(record.periode_id.name + str(record.date_from) + str(record.date_to), "ini yang baru")
        #     record.periode_from_to = record.periode_id.name + " | " + str(record.date_from) + " | " + str(record.date_to)

    def action_reproses(self):
        for data in self:
            # pass
            period_id = data.id
            area_id = data.area_id
            branch_id = data.branch_id

            body = _('Re-Process Period')
            data.message_post(body=body)

            if data.state_process == 'done':
                raise UserError("Sudah Close")

            try:
                self.env.cr.execute("CALL calculate_acc(%s, %s, %s)", (period_id, area_id.id, branch_id.id))
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
            pass
            # tms_summary_data = self.env['hr.tmsentry.summary'].sudo().search([
            #     ('periode_id', '=', rec.id),
            #     ('area_id', '=', rec.area_id.id),
            #     ('branch_id', '=', rec.branch_id.id)
            # ])

            # employee_ids = tms_summary_data.mapped('employee_id.id')

            # hr_employee_data = self.env['hr.employee'].sudo().search([
            #     ('id', 'in', employee_ids)
            # ])

            # employee_dict = {emp.id: emp for emp in hr_employee_data}
            
            # for tsd in tms_summary_data:
            #     employee = employee_dict.get(tsd.employee_id.id)
            #     if employee:
            #         tsd.ot = employee.allowance_ot
            #         tsd.ot_flat = employee.allowance_ot_flat
            #         tsd.night_shift = employee.allowance_night_shift

    def action_opening_periode(self):
        for data in self:
            if not data.open_periode_from or not data.open_periode_to:
                raise UserError(
                    "The 'Periode From' and 'Periode To' fields are required. Please enter values for both fields."
                )
            pass

            period_id = data.id
            area_id = data.area_id
            branch_id = data.branch_id
            body = _('Process Period: %s' % self.state_process)
            data.message_post(body=body)

            # ''' validasi : Seluruh employee group yg sesuai area & branch nya sama dengan
            # area & branch dari proses open period yg sedang dijalankan,
            # harus sudah berstatus approve '''
            # employee_group = self.env['hr.empgroup'].sudo().search([
            #     ('area_id', '=', area_id.id),
            #     ('branch_id', '=', branch_id.id),
            #     ('state', '!=', 'approved')
            # ])

            # if len(employee_group) > 1:
            #     raise UserError('Ensure all employee groups have been approved.')

            try:
                self.env.cr.execute("CALL calculate_tms(%s, %s, %s)", (period_id, area_id.id, branch_id.id))
                self.env.cr.commit()
                _logger.info("Stored procedure executed successfully for period_id: %s", period_id)
            except Exception as e:
                _logger.error("Error calling stored procedure: %s", str(e))
                raise UserError("Error executing the function: %s" % str(e))

            data.isopen = True
            data.state_process = "running"

    def action_closing_periode(self):
        for data in self:
            # pass
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


    # def transfer_payroll(self):
    #     pass

    # def _get_view(self, view_id=None, view_type='form', **options):
    #     arch, view = super()._get_view(view_id, view_type, **options)
        
    #     if view_type in ('tree', 'form'):
    #         group_name = self.env['res.groups'].search([('name','in',['User TMS','HRD CA'])])
    #         cekgroup = self.env.user.id in group_name.users.ids
    #         if cekgroup:
    #             for node in arch.xpath("//field"):
    #                 node.set('readonly', 'True')
    #             for node in arch.xpath("//button"):
    #                 node.set('invisible', 'True')
    #             for node in arch.xpath("//tree"):
    #                 node.set('create', '0')
    #             for node in arch.xpath("//form"):
    #                 node.set('create', '0')
    #     return arch, view