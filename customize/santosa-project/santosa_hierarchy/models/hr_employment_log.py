from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
from dateutil.relativedelta import relativedelta
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
ORDER_STATE = [
    ('draft', "Draft"),
    ('approved', "Approved"),
]


class HrEmployementlog(models.Model):
    _name = 'hr.employment.log'
    _description = 'HR Employement Log'
    _order = 'create_date desc, id desc'

    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    service_type = fields.Char('Tipe Transaksi',)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End date')
    bisnis_unit = fields.Many2one('res.branch', string='Business Units')
    department_id = fields.Many2one('hr.department', string='Sub Department')
    job_title = fields.Char('Jabatan')
    job_status = fields.Selection([('permanent', 'Permanent'),
                                   ('contract', 'Contract'),
                                   ('outsource', 'Out Source')], default='contract', string='Status Hubungan Kerja')
    emp_status = fields.Selection([('probation', 'Probation'),
                                   ('confirmed', 'Confirmed'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('transfer_to_group', 'Transfer To Group'),
                                   ('terminated', 'Terminated'),
                                   ('pass_away', 'Pass Away'),
                                   ('long_illness', 'Long Illness')], default='probation', string='Status Kekaryawanan')
    masa_jabatan = fields.Char('Masa Jabatan', compute='hitung_masa_jabatan', store=False)
    nik = fields.Char('NIK', compute='_get_nik')
    employee_group1 = fields.Char(string="Group Penggajian", compute='_get_nik')
    model_name = fields.Char(string="Model Name")
    model_id = fields.Integer(string="Model Id")
    trx_number = fields.Char(string="Nomor Transaksi")
    doc_number = fields.Char(string="Nomor Dokumen")
    end_contract = fields.Boolean(string="Flag End of Contract", default=False)
    rehire = fields.Boolean(string="Dipanggil Kembali", default=False)
    label = fields.Char(default="Open View")

    def ambil_view(self):
        self.ensure_one()  # Ensure this method is called on a single record
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        target_url = f"{base_url}/web#id={self.model_id}&model={self.model_name}&view_type=form"
        if self.model_name and self.model_id:
            return {
                'type': 'ir.actions.act_url',
                'url': target_url,
                'target': 'self',
            }
        else:
            raise ValidationError("Model Name dan Model ID Belum Terisi!!!")
        # for rec in self:
        #     if rec.model_name and rec.model_id:
        #         return {
        #             'type': 'ir.actions.act_window',
        #             'name': rec.model_name,
        #             'view_mode': 'form',
        #             'res_model': rec.model_name,
        #             'res_id': rec.model_id,
        #             'target': 'current',
        #             'context': {'create': False, 'delete': False, 'edit': False},
        #         }

    @api.onchange('employee_id')
    def _get_nik(self):
        for rec in self:
            if rec.employee_id:
                rec.nik = rec.employee_id.nik
                rec.employee_group1 = rec.employee_id.employee_group1

    @api.depends('start_date', 'end_date')
    def hitung_masa_jabatan(self):
        for record in self:
            service_util = False
            myear = 0
            mmonth = 0
            mday = 0
            if record.employee_id.job_status == 'contract':
                mycont = self.env['hr.contract'].sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('date_end', '<=', record.start_date)], limit=1)
                if mycont:
                    service_until = mycont.date_end
                    if mycont.date_start and service_until > mycont.date_start:
                        service_duration = relativedelta(
                            service_until, mycont.date_start
                        )
                        myear = service_duration.years
                        mmonth = service_duration.months
                        mday = service_duration.days
            else:
                if record.start_date and record.end_date:
                    service_until = record.end_date
                else:
                    service_until = fields.Date.today()
                if record.start_date and service_until > record.start_date:
                    service_duration = relativedelta(
                        service_until, record.start_date
                    )
                    myear = service_duration.years
                    mmonth = service_duration.months
                    mday = service_duration.days
            masajab = 'Year %s Month %s Days %s' % (myear, mmonth, mday)
            record.masa_jabatan = masajab

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view