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
_logger = logging.getLogger(__name__)

class CertificationType(models.Model):
    _name = 'certification.type'
    _description = 'HR Employee Certification Type'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    code = fields.Char(string='Kode',size=3,required=True)
    name = fields.Char(string='Nama' ,required=True, tracking=True)
    active = fields.Boolean(string='Active' , default=True, tracking=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The certification Type must be unique.')
    ]

#     def _get_view(self, view_id=None, view_type='form', **options):
#         arch, view = super()._get_view(view_id, view_type, **options)
#         if view_type in ('tree', 'form'):
#                group_name = self.env['res.groups'].search([('name','=','HRD CA')])
#                cekgroup = self.env.user.id in group_name.users.ids
#                if cekgroup:
#                    for node in arch.xpath("//field"):
#                           node.set('readonly', 'True')
#                    for node in arch.xpath("//button"):
#                           node.set('invisible', 'True')
#         return arch, view
 
    @api.model
    def create(self, vals):
        if 'code' in vals and vals['code']:
            vals['code'] = vals['code'].upper()
        return super(CertificationType, self).create(vals)

    def write(self, vals):
        if 'code' in vals and vals['code']:
            vals['code'] = vals['code'].upper()
        return super(CertificationType, self).write(vals)

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name}"