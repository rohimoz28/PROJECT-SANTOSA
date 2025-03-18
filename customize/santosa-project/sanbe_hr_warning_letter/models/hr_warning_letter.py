# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)
ORDER_STATE = [
    ('draft', "Draft"),
    ('approved', "Approved"),
]
class HRWarningLeter(models.Model):
    _name = 'hr.warning.letter'
    _description = 'HR Checking ID'

    name = fields.Char(
        string="Transaction Number",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    reff_no = fields.Char('Refference Number',index=True)
    emp_no = fields.Many2one('hr.employee',string='Employee No',index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    employee_name = fields.Char(string='Employee Name')
    nik = fields.Char('NIK')
    area = fields.Char('Area')
    bisnis_unit = fields.Char('Bisnis Unit')
    departmentid = fields.Char(string='Sub Department')
    state = fields.Selection(
        selection=ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    warning_type = fields.Many2one('hr.warning.lettertype',string='Waring Letter Type',index=True,ondelete='cascade')
    warning_date = fields.Date('Warning Date')
    pasal_pelanggaran = fields.Many2one('hr.pasal.pelanggaran',string='Pasal Pelanggaran',ondelete='cascade')
    effective_datefrom = fields.Date('Effective Date From')
    effective_dateto = fields.Date('To')
    remarks  = fields.Text('Remarks')
    image =fields.Many2many('ir.attachment', string='Image',
                                          help="You may attach files to with this")

    transaction_date = fields.Date('Transaction Date')
    transaction_status = fields.Char('Trx Status')

    def button_approve(self):
        for allcari in self:
            self.env['hr.employment.log'].sudo().create({'employee_id': allcari.employee_id.id,
                                                         'service_type': allcari.service_type,
                                                         'start_date': allcari.effective_datefrom,
                                                         'end_date': allcari.effective_dateto,
                                                         'bisnis_unit': allcari.employee_id.branch_id.id,
                                                         'department_id': allcari.employee_id.department_id.id,
                                                         'sub_dept': allcari.employee_id.department_id.parent_id.id,
                                                         'job_title': allcari.employee_id.job_id.name,
                                                         'job_status': allcari.employee_id.job_status,
                                                         'emp_status': allcari.employee_id.job_status})

        return self.write({'state': 'approved'})

    def pencarian_data(self):
        return

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.warning.letter') or _('New')
        res = super(HRWarningLeter, self).create(vals)
        # for allres in res:
        #     employee = self.env['hr.employee'].sudo().browse(allres.employee_id.id)
        #     employee.write({'state': 'hold'})
        return res
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