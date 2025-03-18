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
from odoo.exceptions import AccessError, MissingError, UserError
import requests
import logging

_logger = logging.getLogger(__name__)

chari = {'0':6,'1':0,'2':1,'3':2,'4':3,'5':4,'6':5}

class HRTmsOpenClose(models.Model):
    _name = "hr.opening.closing"
    _description = 'HR TMS Open And Close'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # @api.depends('area_id')
    # def _isi_semua_branch(self):
    #     for allrecs in self:
    #         databranch = []
    #         for allrec in allrecs.area_id.branch_id:
    #             mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
    #             databranch.append(mybranch.id)
    #         allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
    #         allrecs.branch_ids=[Command.set(allbranch.ids)]

    @api.depends('branch_id')
    def _isi_semua_branch(self):
        for record in self:
            resbranch = self.env['res.branch'].sudo().search([])
            branch = resbranch.filtered(lambda p: p.id == record.branch_id)
            record.branch_ids = branch.id

    name = fields.Char('Periode Name')
    area_id = fields.Many2one('res.territory',string='Area ID', index=True )
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    branch_id = fields.Many2one('res.branch',string='Bisnis Unit',index=True,domain="[('id','in',branch_ids)]")
    open_periode_from = fields.Date('Opening Periode From')
    open_periode_to = fields.Date('Opening Periode To')
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
                if 'open_periode_from' in vals:
                    br = self.env['res.branch'].sudo().search([('id', '=', vals['branch_id'])])
                    date_obj = datetime.strptime(vals['open_periode_to'], "%Y-%m-%d")
                    vals['name'] = date_obj.strftime("%B %Y") + ' | ' + br['name']
                    check = self.env['hr.tmsentry.summary'].sudo().search([
                        ('branch_id', '=', br.id),
                        ('date_from', '<=', datetime.strptime(str(vals['open_periode_from']),"%Y-%m-%d").date()),
                        ('date_to', '>=', datetime.strptime(str(vals['open_periode_from']), "%Y-%m-%d").date())
                    ])
                    if check:
                        raise UserError('Open Periode From for This Branch Already Used')
                    check = self.env['hr.tmsentry.summary'].sudo().search([
                        ('branch_id', '=', br.id),
                        ('date_from', '<=', datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d").date()),
                        ('date_to', '>=', datetime.strptime(str(vals['open_periode_to']), "%Y-%m-%d").date())])
                    if check:
                        raise UserError('Tanggal period ini sudah di gunakan')
            else:
                raise UserError('Branch or Open Periode From Not Selected')

            existing_record = self.search([('branch_id', '=', vals['branch_id']), ('state_process', '=', 'running')])
            if existing_record:
                raise UserError(_("A record with the same branch and running state already exists."))
        res = super(HRTmsOpenClose, self).create(values)
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

    def reopening(self):
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
                _logger.info("Stored procedure executed successfully for period_id: %s", period_id)
            except Exception as e:
                _logger.error("Error calling stored procedure: %s", str(e))
                raise UserError("Error executing the function: %s" % str(e))

            data.isopen = True
            data.state_process = "running"


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
            summary = self.env['hr.tmsentry.summary'].search([('periode_id','=',data.id)])
            # import pdb
            # pdb.set_trace()
            for record in summary:
                record.write({'state': 'done'})
                attendances = self.env['sb.tms.tmsentry.details'].search([('tmsentry_id','=',record.id)])
                for attn in attendances:
                    attn.write({'status': 'done'})
                permissions = self.env['hr.permission.entry'].search([('periode_id','=',record.periode_id.id)])
                for perm in permissions:
                    perm.write({'permission_status': 'done'})
                overtime = self.env['hr.overtime.planning'].search([('periode_id','=',data.id)])
                for ot in overtime:
                    ot.write({'state': 'done'})

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