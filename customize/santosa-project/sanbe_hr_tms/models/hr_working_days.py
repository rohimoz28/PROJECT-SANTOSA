# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import pytz
from datetime import datetime


class HRWorkingDays(models.Model):
    _name = "hr.working.days"
    _description = 'HR Working Days Setting'
    _rec_name = 'code'

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search(
                    [('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search(
                [('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    code = fields.Char('WD Code', index=True, required=True)
    deskripsi = fields.Char('Description', index=True)
    area_id = fields.Many2one("res.territory", string='Area ID', index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch',
                                  store=False)

    branch_id = fields.Many2one('res.branch', string='Business Units',
                                index=True, domain="[('id','in',branch_ids)]", tracking=True)
    working_day_from = fields.Selection([('0', 'Sunday'),
                                         ('1', 'Monday'),
                                         ('2', 'Tuesday'),
                                         ('3', 'Wednesday'),
                                         ('4', 'Thursday'),
                                         ('5', 'Friday'),
                                         ('6', 'Saturday')], string='Full Day From', default='0')
    working_day_to = fields.Selection([('0', 'Sunday'),
                                       ('1', 'Monday'),
                                       ('2', 'Tuesday'),
                                       ('3', 'Wednesday'),
                                       ('4', 'Thursday'),
                                       ('5', 'Friday'),
                                       ('6', 'Saturday')], string='Full Day To', default='6')
    working_half_from = fields.Selection([('0', 'Sunday'),
                                         ('1', 'Monday'),
                                         ('2', 'Tuesday'),
                                         ('3', 'Wednesday'),
                                         ('4', 'Thursday'),
                                         ('5', 'Friday'),
                                         ('6', 'Saturday')], string='Half Day From')
    working_half_to = fields.Selection([('0', 'Sunday'),
                                        ('1', 'Monday'),
                                        ('2', 'Tuesday'),
                                        ('3', 'Wednesday'),
                                        ('4', 'Thursday'),
                                        ('5', 'Friday'),
                                        ('6', 'Saturday')], string='Half Day To')
    isbasic_wd = fields.Boolean('Basic WD', default=False)
    fullday_from = fields.Float('Hours From')
    fullday_to = fields.Float('Hours To')
    halfday_from = fields.Float('Hours Half Day From')
    halfday_to = fields.Float('Hours Half Day To')
    periode_from = fields.Date('Periode From')
    periode_to = fields.Date('Periode To')

    overtime_ids = fields.One2many(
        'hr.overtime.list', 'workingday_id', auto_join=True, index=True)
    overtimetol_ids = fields.One2many(
        'hr.overtime.tollerance', 'workingday_id', auto_join=True, index=True)
    allowance_ids = fields.One2many(
        'hr.allowance.list', 'workingday_id', auto_join=True, index=True)
    is_active = fields.Boolean('Active')
    is_inactive = fields.Boolean('In Active')
    islabelstate = fields.Char('Status')
    islabelfull = fields.Char('Full')
    isfullday = fields.Boolean('Full Day')
    isfullhalf = fields.Boolean('Full Day And Half Day')
    isholiday = fields.Boolean('Holiday')
    type_hari = fields.Selection([('fday', 'Full Day'), ('fhday', 'Full Day And Half Day'), (
        'hday', 'Holiday'), ('shift', 'Shift')], string='Employee Working Hours')
    isavailabel = fields.Char('Available For')
    available_for = fields.Many2many('res.branch', 'available_for_rel',
                                     string='Available For', domain="[('id','in',branch_ids)]", tracking=True)
    bu3 = fields.Boolean('BU3')
    bu4 = fields.Boolean('BU4')
    bu5 = fields.Boolean('BU5')
    bu6 = fields.Boolean('BU6')
    sbe = fields.Boolean('SBE')
    cwc = fields.Boolean('CWC')
    is_tunjangan = fields.Boolean('Tunjangan/Premi')
    valid_from = fields.Date('Valid From')
    valid_to = fields.Date('To')
    delay_allow = fields.Integer(
        string='Permitted Delays (Minute)', default=10)
    is_ot_holiday = fields.Boolean(
        string='Overtime',
        required=False)
    is_ot_automatic = fields.Boolean(
        string='OT Otomatis',
        required=False)
    total_working_hours = fields.Float('Total Working Hours', default=0.0)
    total_half_hours = fields.Float(
        'Total Working Hours Half Hours', default=0.0)

    @api.onchange("type_hari")
    def _change_type_hari(self):
        for rec in self:
            if rec.type_hari == 'fhday':
                rec.total_half_hours = 0.0

    @api.constrains("total_half_hours", "total_working_hours", "type_hari")
    def _check_total_half_hours(self):
        for rec in self:
            if not rec.type_hari:
                raise ValidationError(
                    _("Please Select Employee Working Hours Type"))
            if rec.total_half_hours and rec.total_half_hours < 0.0:
                raise ValidationError(
                    _("Total jam kerja setengah hari tidak boleh di bawah 0 jam"))
            if rec.total_working_hours and rec.total_working_hours <= 1.0:
                raise ValidationError(
                    _("Total jam kerja tidak boleh di bawah 1 jam"))
            if rec.type_hari == 'fhday':
                if rec.total_half_hours < 1.0 or rec.total_working_hours < 1.0:
                    raise ValidationError(
                        _("Total jam kerja dan jam kerja setengah hari tidak boleh kurang dari 1 jam"))

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', 'in', ['User TMS', 'HRD CA'])])
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


class HROTlist(models.Model):
    _name = "hr.overtime.list"
    _description = 'HR Overtime List'

    workingday_id = fields.Many2one(
        'hr.working.days', string='Working Days List', index=True)
    ot_type = fields.Selection([('automatic', 'Automatic'), ('regular', 'Regular'), (
        'holiday', 'Holiday')], string='OT Type', required=True)
    ot_code = fields.Selection([('aot1', 'AOT1'), ('aot2', 'AOT2'), (
        'aot3', 'AOT3'), ('aot4', 'AOT4')], string='OT Code', required=True)
    ot_from = fields.Float('Time From', required=True)
    ot_to = fields.Float('Time To', required=True)
    ot_auto = fields.Float('Hour Auto')

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', 'in', ['User TMS', 'HRD CA'])])
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

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HROTlist, self).create(vals_list)
        return res

    @api.depends('ot_type')
    @api.onchange('ot_type')
    def cek_holiday(self):
        for rec in self:
            if rec.workingday_id:
                if rec.workingday_id.type_hari != 'hday' and rec.ot_type == 'holiday':
                    raise UserError(
                        'Please Selected Holiday in the section Header Employee Working Hours before Create OT Holidays')


class HROTTollerancelist(models.Model):
    _name = "hr.overtime.tollerance"
    _description = 'HR Overtime Tollerance List'

    workingday_id = fields.Many2one(
        'hr.working.days', string='Working Days List', index=True)
    ot_tollerance_from = fields.Float('Range Time From')
    ot_tollerance_to = fields.Float('To')
    ot_tollerance_result = fields.Float('Results')

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', 'in', ['User TMS', 'HRD CA'])])
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


class AllowanceDeduction(models.Model):
    _name = "hr.allowance.list"
    _description = 'HR Allowance List'

    workingday_id = fields.Many2one(
        'hr.working.days', string='Working Days List', index=True)
    code = fields.Selection([('ashf', 'ASHF - Attendee Premi'),
                             ('ans1', 'ANS1 - Night Shift Allowance 1'),
                             ('ans2', 'ANS2 - Night Shift Allowance 2'),
                             ('atrp', 'ATRP - Transport Allowance'),
                             ('amea', 'AMEA - Meal Allowance')], default='ashf', string='Component Code')
    time_from = fields.Float('Time From')
    time_to = fields.Float('Time To')
    qty = fields.Float('Qty')

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', 'in', ['User TMS', 'HRD CA'])])
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
