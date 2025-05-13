# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

from datetime import date,datetime,timedelta
_logger = logging.getLogger(__name__)

class HrEmployeeCertification(models.Model):
    """Extended model for HR employees with additional features."""
    _name = 'hr.employee.certification'
    _description = 'HR Employee Certification'

    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', index=True, required=True)
    name = fields.Char(string='Nama Sertifikasi',required=True)
    nik = fields.Char(string='Nik',compute="_get_nik", index=True)
    number = fields.Char(string='Nomor Sertifikasi',required=True)
    certification_types = fields.Selection([
        ('formal', 'Formal'),
        ('non_formal', 'Non Formal'),
        ('profesi', 'Profesi')
    ], string='Tipe Sertifikat', index=True, default='formal',
        help="Defines the certification type.")
    certification_types_id = fields.Many2one('certification.type', string='Tipe Sertifikat', index=True,
        help="Defines the certification type.")
    certification_code = fields.Char(related='certification_types_id.code',store=True)
    must = fields.Boolean(string='Wajib',default=False)
    issuing_institution = fields.Char('Institusi Penerbit Sertifikat',required=True)
    valid_from = fields.Date(string='Berlaku mulai', default=fields.Date.today, required=True)
    valid_to = fields.Date(string='Hingga', required=True)
    periode = fields.Char(string='Periode', compute='_compute_periode', store=True)

    @api.depends('valid_from')
    def _compute_periode(self):
        for record in self:
            record.periode = str(record.valid_from.year) if record.valid_from else ''
            
    notification_date = fields.Date(string='Date Notification', compute='_compute_notification_date',store=True)
    skill_id = fields.Many2one('hr.skill','Kompetensi')
    level_skill = fields.Selection([
        ('basic', 'Dasar'),
        ('intermediate', 'Menengah'),
        ('advanced', 'Lanjutan')], default='basic')
    is_dinas = fields.Boolean(string="Ikatan Dinas")
    date_from = fields.Date(string="Ikatan Dinas Dari")
    date_to = fields.Date(string="Ikatan Dinas Hingga")
    remarks = fields.Text(string='Keterangan')
    certificate_attachmentids = fields.Many2many('ir.attachment', string='Lampiran',
                                          help="You may attach files to with this")
    cerv_refrence= fields.Many2one('hr.employee.certification',readonly=True)
    active = fields.Boolean(string="Active", default=True)
    # new_certivicate = fields.Boolean(string="Active", default=True)
    # New field: indicates whether the certificate has an expiration date or not
    is_long_life = fields.Boolean(string="Long Life Certification", 
                                  help="Indicates whether the certificate doesn't expire.")
    
    def unlink(self):
        return super(HrEmployeeCertification, self).unlink()
    
    
    @api.depends('valid_to')
    def _compute_notification_date(self):
        for record in self:
            if record.valid_to and not record.is_long_life:
                # Calculate 30 days before the valid_to date
                record.notification_date = record.valid_to - timedelta(days=30)

    # Computed field to check if the certification is expired
    
    is_expired = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Valid'),
        ('expired', 'Expired')
    ], string="Certification Status", default='draft', compute="_compute_is_expired", store=True)
    
    
    def unlink(self):
        return super(HrEmployeeCertification, self).unlink()
    
    
    @api.depends('certification_types')
    def _certification_types(self):
        for line in self:
            if line.certification_types != 'non_formal':
                line.is_long_life = False
                line.valid_to = date.today()
                
    
    def _compute_is_expired(self):
        """Compute if the certification is expired or has no expiration date."""
        today = date.today()
        for record in self.env['hr.employee.certification'].search([]):
        # for record in self:
            if record.is_long_life:
                record.is_expired = 'valid'  # Long life certifications are considered valid
            else:
                if record.valid_to and record.valid_to < date.today() :
                    record.is_expired = 'expired' 
                else:
                    record.is_expired = 'valid'
                
    @api.model
    def create(self, vals):
        """Override create to set valid_to for long life certifications."""
        if vals.get('is_long_life'):
            vals['valid_to'] = '2999-12-31'
        return super(HrEmployeeCertification, self).create(vals)

    def write(self, vals):
        """Override write to set valid_to for long life certifications."""
        if 'is_long_life' in vals and vals['is_long_life']:
            vals['valid_to'] = '2999-12-31'
        return super(HrEmployeeCertification, self).write(vals)

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
    
    def set_toDraft(self):
        self.is_expired = 'draft'
    
    def set_reactiv(self):
        self.is_expired = 'valid'
    
    def renewal_certivicate(self):
        self.active = False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.certification',
            'view_mode': 'form',
            'target': 'new',  # This makes it open as a pop-up
            'context': {'employee_id': self.employee_id.id,
                        'must':self.must,
                        'skill_id':self.skill_id,
                        'certification_types':self.certification_types,
                        'valid_from':date.today(),
                        'cerv_refrence':self.id}
        }