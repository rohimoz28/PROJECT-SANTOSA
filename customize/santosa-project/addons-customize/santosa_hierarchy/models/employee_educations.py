from odoo import api, fields, models, _
class EducationLevel(models.Model):
    _name = 'employee.educations'
    _description = "Employee Education"
    _rec_name = 'name'

    employee_id = fields.Many2one('hr.employee',string='Employee ID',index=True)
    school_level = fields.Selection([('universitas','Perguruan Tinggi'),
                                     ('sma','SMA'),
                                     ('smp','SMP'),
                                     ('sd','SD')],default='universitas',string='Jenjang Pendidikan')
    name = fields.Char('Nama Sekolah')
    year_graduated = fields.Char('Tahun Pendidikan')
    majoring= fields.Char('Bidang Studi')
    level_certificated = fields.Selection([('s3','S3'),
                                     ('sma','SMA'),
                                     ('d1','D1'),
                                     ('d2','D2'),
                                     ('d3','D3'),
                                     ('s1','Sarjana'),
                                     ('s2','Magister'),
                                     ('s3','Doktor'),
                                     ],default='s1',string='Ijasah Terakhir')
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