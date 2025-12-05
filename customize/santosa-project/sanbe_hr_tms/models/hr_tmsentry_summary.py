# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
import pdb

from odoo import fields, models, api, _, Command
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import pytz
from datetime import date, datetime, time, timedelta

TMS_ENTRY_STATE = [
    ('draft', 'Draft'),
    ('running', 'Running'),
    ('approved', "Approved"),
    ('done', "Close"),
    ('transfer_payroll', 'Transfer Payroll'),
]

EMP_GROUP1 = [
    ('Group1', 'Group 1 - Harian(pak Deni)'),
    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
    ('Group4', 'Group 4 - Security and non apoteker (bu Susi)'),
    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
    ('Group7', 'Group 7 - Tim Proyek (pak Ferry)'),
]


class HRTMSEntrySummary(models.Model):
    _name = "hr.tmsentry.summary"
    _description = 'HR TMS Entry Summary'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    def _default_employee(self):
        return self.env.user.employee_id

    def _get_active_periode_from(self):
        mycari = self.env['hr.opening.closing'].sudo().search([('isopen', '=', True)], limit=1)
        return mycari.open_periode_from or False

    def _get_active_periode_to(self):
        mycari = self.env['hr.opening.closing'].sudo().search([('isopen', '=', True)], limit=1)
        return mycari.open_periode_to or False

    periode_id = fields.Many2one('hr.opening.closing', string='Periode', index=True)
    employee_id = fields.Many2one('hr.employee', string="Nama", default=_default_employee, required=True,
                                  ondelete='cascade', index=True, readonly="state =='done'")
    employee_name = fields.Char('Employee Name', related='employee_id.name', store=True)
    area_id = fields.Many2one('res.territory', string='Area', index=True, readonly="state =='done'")
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True, domain="[('id','in',branch_ids)]",
                                readonly="state =='done'")
    department_id = fields.Many2one('hr.department', string='Sub Department', readonly="state =='done'")
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    max_ot = fields.Float('Jam Lembur Maksimal', related='employee_id.max_ot', digits=(16, 1), store=True)
    max_ot_month = fields.Float(string='Max OT / bulan', related='employee_id.max_ot_month', digits=(16, 1), store=True)
    nik = fields.Char('NIK')
    job_id = fields.Many2one('hr.job', string='Jabatan', readonly="state =='done'")
    date_from = fields.Date('Periode From', readonly="state =='done'", related='periode_id.open_periode_from')
    date_to = fields.Date('Periode To', readonly="state =='done'", related='periode_id.open_periode_to')
    tmsentry_ids = fields.One2many('hr.attendance', 'tmsentry_id', auto_join=True, readonly="state =='done'")
    state = fields.Selection(
        selection=TMS_ENTRY_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        # compute='_cek_for_tmsentry_status',
        store=True,
        default='draft')
    attendee_count = fields.Integer('Attendee')
    absent_count = fields.Integer('Absent')
    delay_total = fields.Integer('Total Delay',help="Total Delay in Minutes")
    employee_group1s = fields.Many2one('emp.group', string='Employee Group', related='employee_id.employee_group1s', tracking=True, store=True)

    attendee_total = fields.Integer('Total Attendee')
    sick_count = fields.Integer('Total Sick')
    leave_count = fields.Integer(string='Total Leave')
    permission_count = fields.Integer('Permission', compute='_hitung_total_data', store=False, precompute=True)
    outstation_count = fields.Integer('Out Station', compute='_hitung_total_data', store=False, precompute=True)
    ot1_count = fields.Integer('OT1', compute='_hitung_total_data', store=False, precompute=True)
    ot2_count = fields.Integer('OT2', compute='_hitung_total_data', store=False, precompute=True)
    ot3_count = fields.Integer('OT3', compute='_hitung_total_data', store=False, precompute=True)
    ot4_count = fields.Integer('OT4', compute='_hitung_total_data', store=False, precompute=True)
    ot1_total = fields.Float('Total OT1x', compute='_hitung_total_data', store=False, precompute=True)
    ot2_total = fields.Float('Total OT2x', compute='_hitung_total_data', store=False, precompute=True)
    ot3_total = fields.Float('Total OT3x', compute='_hitung_total_data', store=False, precompute=True)
    ot4_total = fields.Float('Total OT4x', compute='_hitung_total_data', store=False, precompute=True)
    ot_auto_count = fields.Integer('OT Auto', compute='_hitung_total_data', store=False, precompute=True)
    ot_auto_total = fields.Float('Total OT Autox', compute='_hitung_total_data', store=False, precompute=True)
    ot1_totalx = fields.Float(string='Total OT1')
    ot2_totalx = fields.Float(string='Total OT2')
    ot3_totalx = fields.Float(string='Total OT3')
    ot4_totalx = fields.Float(string='Total OT4')
    ot_auto_totalx = fields.Float('Total OT Auto', compute='_hitung_total_data', store=False, precompute=True)
    delay_count = fields.Float('Delay', help='Total Times Delayed')
    total_workingday = fields.Integer(
        string='Total Workingday',
        required=False)
    pattendace_count = fields.Integer('Premi Attendance')
    transport_count = fields.Integer(string='Transport Allowance')
    nightshift_count = fields.Integer(string='Night Shift')
    nightshift2_count = fields.Integer(string='Night Shift')
    meal_count = fields.Integer(string='Meal')
    is_deduction = fields.Boolean('Deducton', default=False)
    deduction = fields.Integer('total deductions (days)', default=0)
    total_deduction = fields.Float(
        string='Total Deduction',
        required=False)
    tmsentry_details_ids = fields.One2many(
        comodel_name='sb.tms.tmsentry.details',
        inverse_name='tmsentry_id',
        string='TMS Summary Details',
        required=False)

    #untuk domain pada pages di tms
    tmsentry_details_10_ids = fields.One2many(
        comodel_name='sb.tms.tmsentry.details',
        inverse_name='tmsentry_id',
        domain=[('flag', 'ilike', '10')],
        string='TMS Summary Details',
        required=False)
    tmsentry_details_20_ids = fields.One2many(
        comodel_name='sb.tms.tmsentry.details',
        inverse_name='tmsentry_id',
        domain=[('flag', 'ilike', '20')],
        string='TMS Summary Details',
        required=False)
    tmsentry_details_30_ids = fields.One2many(
        comodel_name='sb.tms.tmsentry.details',
        inverse_name='tmsentry_id',
        domain=[('flag', 'ilike', '30')],
        string='TMS Summary Details',
        required=False)
    tmsentry_details_40_ids = fields.One2many(
        comodel_name='sb.tms.tmsentry.details',
        inverse_name='tmsentry_id',
        domain=[('flag', 'ilike', '40')],
        string='TMS Summary Details',
        required=False)
    tmsentry_details_50_ids = fields.One2many(
        comodel_name='sb.tms.tmsentry.details',
        inverse_name='tmsentry_id',
        domain=[('flag', 'ilike', '50')],
        string='TMS Summary Details',
        required=False)

    is_deduction_desc = fields.Text(
        string="Keterangan PG",
        required=False)
    total_late_deduction = fields.Float(string='Total Potongan Akumulasi Terlambat')
    # hrd_approved = fields.Boolean(
    #     string='HRD Approved',
    #     compute='_is_all_approved_by_ca',
    #     default=False,
    #     required=False)
    # checker_approved = fields.Boolean(
    #     string='CA Approved',
    #     compute='_is_all_approved_by_ca',
    #     default=False,
    #     required=False)
    # employee_group1 = fields.Selection(selection=EMP_GROUP1,string='Employee P Group')
    completed_hrd = fields.Integer(
        string='Completed Approval HRD',
        compute='_task_progress_approval',
        store=True,
        required=False)
    completed_ca = fields.Integer(
        string='Completed Approval CA',
        compute='_task_progress_approval',
        store=True,
        required=False)
    task_hrd = fields.Integer(
        string='Tasks Approval HRD',
        compute='_task_progress_approval',
        store=True,
        required=False)
    task_ca = fields.Integer(
        string='Tasks Approval CA',
        compute='_task_progress_approval',
        store=True,
        required=False)
    task_progress_ca = fields.Char(
        string="Progress CA Approved",
        compute="_compute_progress_approval_ca"
    )
    task_progress_hrd = fields.Char(
        string="Progress HRD Approved",
        compute="_compute_progress_approval_hrd"
    )
    ot = fields.Boolean(compute='_compute_ot', store=True)
    ot_flat = fields.Boolean(compute='_compute_ot_flat', store=True)
    night_shift = fields.Boolean(compute='_compute_night_shift', store=True)

    periode_from_to = fields.Char(compute='_compute_concate', store=True)

    @api.depends('periode_id','date_from','date_to')
    def _compute_concate(self):
        print("MULAI CONCATE")
        for record in self:
            print(record.periode_id.name + str(record.date_from) + str(record.date_to), "ini yang baru")
            record.periode_from_to = record.periode_id.name + " | " + str(record.date_from) + " | " + str(record.date_to)
    
    @api.depends('employee_id.allowance_ot')
    def _compute_ot(self):
        for record in self:
            record.ot = record.employee_id.allowance_ot
    
    @api.depends('employee_id.allowance_ot_flat')
    def _compute_ot_flat(self):
        for record in self:
            record.ot_flat = record.employee_id.allowance_ot_flat
    
    @api.depends('employee_id.allowance_night_shift')
    def _compute_night_shift(self):
        for record in self:
            record.night_shift = record.employee_id.allowance_night_shift
    
    def btn_export_to_excel(self):
        print('ieu')

    @api.depends('tmsentry_details_ids')
    def _task_progress_approval(self):
        for rec in self:
            rec.completed_hrd = sum(rec.tmsentry_details_ids.mapped('approved'))
            rec.completed_ca = sum(rec.tmsentry_details_ids.mapped('approved_by_ca'))
            rec.task_ca = len(rec.tmsentry_details_ids.mapped('approved_by_ca'))
            rec.task_hrd = len(rec.tmsentry_details_ids.mapped('approved'))

    @api.depends('tmsentry_details_ids')
    def _compute_progress_approval_hrd(self):
        for rec in self:
            # approvals = rec.tmsentry_details_ids.mapped('approved')
            task_total = rec.task_hrd
            task_done = rec.completed_hrd
            rec.task_progress_hrd = f"{task_done}/{task_total}" if task_total else "0/0"

    @api.depends('tmsentry_details_ids')
    def _compute_progress_approval_ca(self):
        for rec in self:
            # approvals = rec.tmsentry_details_ids.mapped('approved_by_ca')
            task_total = rec.task_ca
            task_done = rec.completed_ca
            rec.task_progress_ca = f"{task_done}/{task_total}" if task_total else "0/0"

    @staticmethod
    def last_even_divided_by_2(number):
        if number == 1:
            return 1
        last_even = number if number % 2 == 0 else number - 1
        return last_even // 2

    # @api.depends('tmsentry_details_ids')
    # def _calculate_deduction(self):
    #     for rec in self:
    #         rec.is_deduction = bool(rec.delay_count and rec.delay_total)
    #         total_delay_level1 = sum(rec.tmsentry_details_ids.mapped('delay_level1'))
    #         total_delay_level2 = sum(rec.tmsentry_details_ids.mapped('delay_level2'))
    #         calculate_total_delay_level1 = self.last_even_divided_by_2(total_delay_level1) * 0.5
    #         calculate_total_delay_level2 = total_delay_level2 * 0.5
    #         total = calculate_total_delay_level1 + calculate_total_delay_level2
    #         rec.total_deduction = total

    def _getwaktu(self, waktu):
        ret = timedelta()
        for i in waktu:
            x = str(self.ubahjam(i))
            (h, m, s) = x.split(':')
            d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            ret += d
        return ret

    def _getwaktu2(self, waktu):
        ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m))
        ret += d
        return ret

    def _getwaktu4(self, waktu):
        ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        ret += d
        return ret

    def _getwaktu3(self, waktu):
        # ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        ret = self._getfloat(d)
        return ret

    def ubahjam(self, hours_float):
        midnight = datetime.combine(date.today(), time.min)
        time_delta = timedelta(hours=hours_float)
        time_obj = (midnight + time_delta).time()
        return time_obj

    def ubahjam2(self, waktu):
        detik = waktu * 3600
        hours = divmod(detik, 3600)[0]  # split to hours and seconds
        sisad = detik - (hours * 3600)
        minutes = divmod(sisad, 60)[0]
        seconds = sisad - (minutes * 60)
        # result = '{0:02.0f}:{1:02.0f}'.format(*divmod(waktu * 60, 60))
        result = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(hours, minutes, seconds)
        return result

    def _getjam(self, jam):
        ret = None
        detik = jam.total_seconds()
        hour = divmod(detik, 3600)[0]
        sisad = detik - (hour * 3600)
        minute = divmod(sisad, 60)[0]
        second = sisad - (minute * 60)
        ret = str(hour) + ":" + minute + ":" + second
        return ret

    def _getfloat(self, jam):
        ret = None
        detik = jam.total_seconds()
        hour = divmod(detik, 3600)[0]
        minute = divmod(detik, 3600)[1] / 3600
        # hour = divmod(detik,3600)[0]
        # sisad = detik - (hour * 3600)
        # minute = divmod(sisad,60)[0]
        # second = sisad - (minute * 60)
        ret = hour + minute
        return ret

    def mass_approve(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['hr.tmsentry.summary'].browse(selected_ids)
        attendance_records = self.env['sb.tms.tmsentry.details'].sudo().search([('tmsentry_id', 'in', selected_records.ids)])
        approval_type = self.env.context.get('approval_type')
        not_approved_hrd = attendance_records.filtered(lambda r: not r.approved)
        not_approved_ca = attendance_records.filtered(lambda r: not r.approved_by_ca)

        for record in self:
            if approval_type == 'hrd':
                for rec in attendance_records:
                    rec.approved = True
                # record.hrd_approved = True
                self._task_progress_approval()
                self.env.cr.commit()
            elif approval_type == 'checker':
                # if not record.hrd_approved:
                #     raise ValidationError("HRD Not Approved")
                # not_approved_h = attendance_records.filtered(lambda r: not r.approved)
                
                # if not_approved_hrd:
                #     raise ValidationError("HRD Not Approved")
                
                for rec in attendance_records:
                    rec.approved_by_ca = True
                # record.checker_approved = True
                self._task_progress_approval()
                self.env.cr.commit()
            elif approval_type == 'approved':
                # if not record.hrd_approved or not record.checker_approved:
                #     raise ValidationError("HRD & CA Not Approved")
                # for rec in attendance_records:
                #     if rec.approved is False:
                #         raise ValidationError("HRD Not Approved")
                #     if rec.approved_by_ca is False:
                #         raise ValidationError("CA Not Approved")
                #     if rec.approved is False and rec.approved_by_ca is False:
                #         raise ValidationError("HRD & CA Not Approved")
                    # rec.state = 'approved'
                
                # not_approved_h = attendance_records.filtered(lambda r: not r.approved)
                # not_approved_ca = attendance_records.filtered(lambda r: not r.approved_by_ca)

                if not_approved_hrd and not_approved_ca:
                    raise ValidationError("HRD & CA Not Approved")
                elif not_approved_hrd:
                    raise ValidationError("HRD Not Approved")
                elif not_approved_ca:
                    raise ValidationError("CA Not Approved")
                
                record.state = 'approved'
                self.env.cr.commit()

    @api.depends('tmsentry_ids', 'state')
    def _hitung_total_data(self):
        for rec in self:
            # attende = rec.tmsentry_ids.filtered(
            #     lambda p: p.attendence_status in ['attendee', 'delay_in', 'leave', 'outstation'] and p.day_type == 'w')
            # rec.attendee_count = len(attende)
            # import pdb
            # pdb.set_trace()

            sicks = rec.tmsentry_ids.filtered(lambda p: p.attendence_status == 'sick' and p.day_type == 'w')
            # absent = rec.tmsentry_ids.filtered(lambda p: p.attendence_status == 'absent' and p.day_type == 'w')
            leaves = rec.tmsentry_ids.filtered(lambda p: p.attendence_status == 'leave' and p.day_type == 'w')
            permission = rec.tmsentry_ids.filtered(lambda p: p.permision_code != False)
            outstation = rec.tmsentry_ids.filtered(lambda p: p.attendence_status == 'outstation' and p.day_type == 'w')
            rec.sick_count = len(sicks)
            # rec.absent_count = len(absent)
            rec.leave_count = len(leaves)
            rec.permission_count = len(permission)
            rec.outstation_count = len(outstation)

            dataot1 = rec.tmsentry_ids.filtered(lambda p: p.ot1 != False)
            tot1x = (dataot1.mapped('ot1_time'))
            tot1xx = sum(dataot1.mapped('ot1_timex'))
            tot1 = self._getfloat(self._getwaktu(tot1x))
            rec.ot1_count = len(dataot1)
            rec.ot1_total = tot1
            rec.ot1_totalx = tot1xx

            dataot2 = rec.tmsentry_ids.filtered(lambda p: p.ot2 != False)
            tot2x = (dataot2.mapped('ot2_time'))
            tot2xx = sum(dataot2.mapped('ot2_timex'))
            tot2 = self._getfloat(self._getwaktu(tot2x))
            rec.ot2_count = len(dataot2)
            rec.ot2_total = tot2
            rec.ot2_totalx = tot2xx

            dataot3 = rec.tmsentry_ids.filtered(lambda p: p.ot3 != False)
            tot3x = (dataot3.mapped('ot3_time'))
            tot3xx = sum(dataot3.mapped('ot3_timex'))
            tot3 = self._getfloat(self._getwaktu(tot3x))
            rec.ot3_count = len(dataot3)
            rec.ot3_total = tot3
            rec.ot3_totalx = tot3xx

            dataot4 = rec.tmsentry_ids.filtered(lambda p: p.ot4 != False)
            tot4x = (dataot4.mapped('ot4_time'))
            tot4xx = sum(dataot4.mapped('ot4_timex'))
            tot4 = self._getfloat(self._getwaktu(tot4x))
            rec.ot4_count = len(dataot4)
            rec.ot4_total = tot4
            rec.ot4_totalx = tot4xx

            dataot_auto = rec.tmsentry_ids.filtered(lambda p: p.ot_auto != False)
            tot_autox = (dataot_auto.mapped('ot_auto_time'))
            tot_autoxx = sum(dataot_auto.mapped('ot_auto_timex'))
            tot_auto = self._getfloat(self._getwaktu(tot_autox))
            rec.ot_auto_count = len(dataot_auto)
            rec.ot_auto_total = tot_auto
            rec.ot_auto_totalx = tot_autoxx

            datapatt = rec.tmsentry_ids.filtered(lambda p: p.premi_attendee != False)
            datatrans = rec.tmsentry_ids.filtered(lambda p: p.tunjangan_trp != False)
            datanight = rec.tmsentry_ids.filtered(lambda p: p.night_shift != False)
            rec.pattendace_count = len(datapatt)
            rec.transport_count = len(datatrans)
            rec.nightshift_count = len(datanight)

            total_delay_level1 = rec.tmsentry_ids.filtered(lambda p: p.delay_level1 != False)
            total_delay_level2 = rec.tmsentry_ids.filtered(lambda p: p.delay_level2 != False)
            # datadelay = rec.tmsentry_ids.filtered(lambda p: p.delayed != False)
            # tdelayx = (datadelay.mapped('delayed'))
            # tdelay = self._getfloat(self._getwaktu(tdelayx))
            rec.delay_count = len(total_delay_level1) + len(total_delay_level2)
            # rec.delay_total = tdelay

            tatt = timedelta()
            tattx = ((rec.tmsentry_ids.filtered(lambda p: p.add_hour != False)).mapped('add_hour'))

            if tattx and tattx != '' and tattx != False:
                tatt = self._getfloat(self._getwaktu(tattx))
            rec.attendee_total = tatt
        return

    def btn_toapproved(self):
        for rec in self:
            records = self.env['sb.tms.tmsentry.details'].sudo().search([('tmsentry_id', '=', rec.id)])
            for record in records:
                if record.approved is False:
                    raise ValidationError("Not Yet Checked by HRD")
                if record.approved_by_ca is False:
                    raise ValidationError("Not Yet Approved by CA")
            rec.state = 'approved'

    def btn_draft(self):
        for rec in self:
            rec.state = 'draft'

    def transfer_payroll(self):
        pass
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'hr.transfer.payroll',
        #     'views': [(False, 'form')],
        #     'view_id': False,
        #     'target': 'new',
        #     'res_id': self.id,
        #     'context': False,
        # }

    def action_done(self):
        for record in self:
            record.state = 'transfer_payroll'

    # def unlink(self):
    #     self = self.sudo()
    #     for allrec in self:
    #         if allrec.state != 'draft':
    #             raise UserError('Cannot Delete Data That Not in Draft State')
    #         for alldet in allrec.tmsentry_ids:
    #             alldet.unlink()
    #     return super(HRTMSEntrySummary, self).unlink()
    #
    # def _get_view(self, view_id=None, view_type='form', **options):
    #     arch, view = super()._get_view(view_id, view_type, **options)
    #     if view_type in ('tree', 'form'):
    #         group_name = self.env['res.groups'].search([('name', '=', 'HRD CA')])
    #         cekgroup = self.env.user.id in group_name.users.ids
    #         if cekgroup:
    #             for node in arch.xpath("//field"):
    #                 node.set('readonly', 'True')
    #             for node in arch.xpath("//button"):
    #                 node.set('invisible', 'True')
    #     return arch, view
    #
    def action_calculation(self):
        pass



class HRTMSEntry(models.Model):
    _name = "hr.tms.entry"
