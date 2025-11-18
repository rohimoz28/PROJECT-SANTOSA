from odoo import fields, models, tools


class HrJobView(models.Model):
    _auto = False
    _name = 'hr.job.view'
    _description = 'HR Job View SQL'
    _order = 'name'

    id = fields.Integer(string='ID', required=True)
    name = fields.Char(string='Jabatan')
    area_id = fields.Many2one('res.territory', string='Area')
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis')
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat')
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen')
    division_id = fields.Many2one('sanhrms.division', string='Divisi')
    active = fields.Boolean(default=True)


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                select 
                    hj.id as id,
                    hj.name->>'en_US' as name,
                    hj.area as area_id,
                    hj.branch_id,
                    hj.directorate_id,
                    hj.hrms_department_id,
                    hj.division_id,
                    hj.active
                from hr_job hj 
            )
        """ % self._table)








