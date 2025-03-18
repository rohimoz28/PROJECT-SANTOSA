# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
class EducationLevel(models.Model):
    _name = 'employee.educations'
    _description = "Employee Education"
    _rec_name = 'name'

    employee_id = fields.Many2one('hr.employee',string='Employee ID',index=True)
    school_level = fields.Selection([('universitas','Perguruan Tinggi'),
                                     ('sma','SMA'),
                                     ('smp','SMP'),
                                     ('sd','SD')],default='universitas',string='School Level')
    name = fields.Char('School Name')
    year_garduated = fields.Char('Year')
    majoring= fields.Char('Majoring')
    level_certificated = fields.Selection([('s3','S3'),
                                     ('s2','S2'),
                                     ('s1','S1'),
                                     ('d3','D3'),
                                     ('d4', 'D4'),
                                     ('sma','SMA'),
                                     ('smp','SMP'),
                                     ('sd','SD')],default='s1',string='Certificate Level')
    gpa = fields.Float('GPA')
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