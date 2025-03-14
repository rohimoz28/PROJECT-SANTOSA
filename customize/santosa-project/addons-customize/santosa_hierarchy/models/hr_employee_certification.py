from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class HrEmployeeCertification(models.Model):
    """Extended model for HR employees with additional features."""
    _name = 'hr.employee.certification'
    _description = 'HR Employee Certification'

    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True, required=True)
    name = fields.Char(string='Certification Name')
    number = fields.Char(string='Certification Number')
    certification_types = fields.Selection([
        ('formal', 'Formal'),
        ('non_formal', 'Non Formal'),
        ('profesi', 'Profesi')
    ], string='Certificate Type', index=True, default='formal',
        help="Defines the certification type.")
    must = fields.Boolean(string='Must',default=False)
    issuing_institution = fields.Char('Issuing Institution')
    valid_from = fields.Date(string='Valid From')
    valid_to = fields.Date(string='Valid To')
    remarks = fields.Text(string='Remarks')
    certificate_attachmentids = fields.Many2many('ir.attachment', string='Attachment',
                                          help="You may attach files to with this")

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