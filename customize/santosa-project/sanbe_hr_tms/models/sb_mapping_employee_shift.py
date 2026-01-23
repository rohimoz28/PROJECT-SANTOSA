# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pytz
from datetime import timedelta, datetime, time, date

_logger = logging.getLogger(__name__)


class SbMappingEmployeeShift(models.Model):
    _name = 'sb.mapping_employee.shift'
    _description = 'Employee Shift Mapping'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin', 'utm.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Name',
        default='New',
        index=True,
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        index=True,
        required=True,
        domain="[('area', '=', area_id), ('branch_id', '=', branch_id), ('state', '=', 'approved')]"
    )

    # Related fields - Disarankan store=True hanya jika diperlukan untuk filtering/reporting
    nik = fields.Char(
        related='employee_id.nik',
        string='NIK',
        store=True,
        readonly=True
    )
    employee_name = fields.Char(
        related='employee_id.name',
        string='Employee Name',
        index=True,
        readonly=True,
        domain=[('wd_type', '=', 'shift')]

    )
    branch_id = fields.Many2one(
        'res.branch',  # Pastikan nama model branch Anda benar, biasanya res.branch
        related='employee_id.branch_id',
        string='Bisnis Unit',
        store=True,
        index=True,
        readonly=True,
        default=lambda self: self.env.user.branch_id.id
    )
    area_id = fields.Many2one(
        'res.territory',  # Sesuaikan dengan model area/territory Anda
        related='employee_id.area',
        string='Area ID',
        store=True,
        index=True,
        readonly=True,
        default=lambda self: self.env.user.branch_id.territory_id.id
    )
    directorate_id = fields.Many2one(
        related='employee_id.directorate_id',
        string='Direktorat',
        store=True,
        index=True,
        readonly=True)
    hrms_department_id = fields.Many2one(
        related='employee_id.hrms_department_id',
        string='Departemen',
        store=True,
        index=True,
        readonly=True)
    division_id = fields.Many2one(
        related='employee_id.division_id',
        string='Divisi',
        store=True,
        readonly=True
    )
    job_id = fields.Many2one(
        related='employee_id.job_id',
        string='Job Position',
        store=True,
        readonly=True
    )
    jabatan = fields.Char(
        related='job_id.name',
        string='Jabatan',
        store=True,
        readonly=True
    )

    work_unit_ids = fields.Many2many(
        'mst.group.unit.pelayanan',
        string='Work Unit',
        compute='_compute_work_unit_ids',
        store=True)

    @api.depends('employee_id.work_unit_ids')
    def _compute_work_unit_ids(self):
        for rec in self:
            rec.work_unit_ids = rec.employee_id.work_unit_ids

    nurse = fields.Many2one(
        'hr.profesion.nurse',
        string='Profesi Perawat',
        related='employee_id.nurse',
        readonly=True,
        tracking=True
    )
    medic = fields.Many2one(
        'hr.profesion.medic',
        'Profesi Medis',
        related='employee_id.medic',
        readonly=True,
        tracking=True
    )
    speciality = fields.Many2one(
        'hr.profesion.special',
        'Kategori Khusus',
        related='employee_id.seciality',
        readonly=True,
        tracking=True
    )
    profesion = fields.Char(
        'Profesi', compute="_compute_profesion", store=True)

    @api.onchange("employee_id")
    @api.depends('nurse', 'medic', 'speciality')
    def _compute_profesion(self):
        for rec in self:
            rec.profesion = False
            if rec.employee_id:
                if rec.medic:
                    rec.profesion = rec.medic.code
                if rec.nurse:
                    rec.profesion = rec.nurse.code
                if rec.speciality:
                    rec.profesion = rec.speciality.code

    shift_id = fields.Many2one(
        'sb.group.shift',
        string='Shift Group',
        store=True,
        required=True,
        tracking=True
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

    _sql_constraints = [
        # ('unique_employee_shift', 'unique(employee_id, shift_id)',
        #  'Employee sudah terdaftar di shift ini!')
        ('unique_employee_mapping_shift', 'unique(employee_id)',
         'Employee sudah terdaftar!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            shift_name = ""
            if vals.get('shift_id'):
                shift = self.env['sb.group.shift'].browse(vals.get('shift_id'))
                shift_name = shift.name or ""

            employee_name = ""
            if vals.get('employee_id'):
                employee = self.env['hr.employee'].browse(
                    vals.get('employee_id'))
                employee_name = employee.name or ""

            # Penentuan Nama Record
            if shift_name and employee_name:
                vals['name'] = f"{shift_name} : {employee_name}"
            elif employee_name:
                vals['name'] = employee_name

        return super(SbMappingEmployeeShift, self).create(vals_list)

    @api.onchange("active", "shift_id", "employee_id")
    def _change_shift_group(self):
        """
        Memberikan feedback instan pada UI dan memperbarui data shift 
        pada periode yang sedang berjalan jika statusnya masih Draft.
        """
        if not self.employee_id:
            return

        user_branch_id = self.env.user.branch_id.id
        periode_id = self.env['hr.opening.closing'].search([
            ('state_process', '=', 'running'),
            ('branch_id', '=', user_branch_id)
        ], order='id desc', limit=1)
        if periode_id:
            # data_shifts = self.env['sb.employee.shift'].search([
            #     ('periode_id', '=', periode_id.id),
            #     ('employee_id', '=', self.employee_id.id),
            #     ('state', '=', 'draft')
            # ])
            data_shifts = self.env['sb.employee.shift'].search([
                ('periode_id', '=', periode_id.id),
                ('employee_id', '=', self.employee_id.id),
            ])

            if data_shifts:
                for shift in data_shifts:
                    if self.active:
                        shift.group_shift = self.shift_id.name
                    else:
                        shift.group_shift = False
            # else:
            #     raise UserError(
            #         f"Tidak ditemukan data shift 'Draft' untuk employee {self.employee_id.name}")
        else:
            raise UserError(
                f"Tidak ditemukan periode Running untuk branch {user_branch_id}")

    def write(self, vals):
        res = super(SbMappingEmployeeShift, self).write(vals)
        user_branch_id = self.env.user.branch_id.id
        for rec in self:
            periode_id = self.env['hr.opening.closing'].search([
                ('state_process', '=', 'running'),
                ('branch_id', '=', user_branch_id)
            ], order='id desc', limit=1)
            if periode_id:
                shifts = self.env['sb.employee.shift'].search([
                    ('periode_id', '=', periode_id.id),
                    ('employee_id', '=', rec.employee_id.id),
                    # ('state', '=', 'draft'),
                ])
                if shifts:
                    if rec.active:
                        shifts.write({'group_shift': rec.shift_id.name})
                    else:
                        shifts.write({'group_shift': False})
            else:
                raise UserError(
                    f"Tidak ditemukan periode Running untuk branch {user_branch_id}")
        return res

    def unlink(self):
        """
        Saat record mapping dihapus, hapus juga referensi group_shift 
        pada transaksi shift yang masih berstatus 'draft'.
        """
        for rec in self:
            user_branch_id = self.env.user.branch_id.id
            periode_id = self.env['hr.opening.closing'].search([
                ('state_process', '=', 'running'),
                ('branch_id', '=', user_branch_id)
            ], order='id desc', limit=1)
            if periode_id:
                shifts = self.env['sb.employee.shift'].search([
                    ('periode_id', '=', periode_id.id),
                    ('employee_id', '=', rec.employee_id.id),
                ])
                if shifts:
                    shifts.write({'group_shift': False})

        return super(SbMappingEmployeeShift, self).unlink()
