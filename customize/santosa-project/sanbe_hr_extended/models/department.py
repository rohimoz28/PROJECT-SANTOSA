from odoo import models, fields, api

class Department(models.Model):
    _name = 'sanhrms.department' # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Santosa Department Hierarchy'

    department_code = fields.Char('Department Code')
    name = fields.Char('Department Name')
    branch_id = fields.Many2one('res.branch',string='Unit Bisnis')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Directorate',required=True)
    directorate_code = fields.Char('Directorate Code',related='directorate_id.directorate_code', store=True)
    division_ids = fields.Many2many('sanhrms.division',string='Division')
    active = fields.Boolean('Active', default=True )
    
    @api.depends('department_code','name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name}"
            account.display_name = '%s-%s' % (account.department_code   or '', account.name)
    
    def unlink(self):
        return super(Department, self).unlink()

    #Saat buat record baru dan milih direktorat maka di direktorat nya akan terpilih department nya
    @api.model
    def create(self, vals):
        department = super(Department, self).create(vals)
        if 'directorate_id' in vals and not self.env.context.get('from_directorate'):
            department.directorate_id.with_context(from_directorate=True).write({'department_ids': [(4, department.id)]})
        return department

    def write(self, vals):
        old_directorate_map = {department.id: department.directorate_id for department in self}

        res = super(Department, self).write(vals)

        if 'directorate_id' in vals:
            for department in self:
                if department.directorate_id:
                    department.directorate_id.with_context(from_department=True).write({'department_ids': [(4, department.id)]})
                
                old_directorate = old_directorate_map.get(department.id)
                if old_directorate and old_directorate != department.directorate_id:
                    old_directorate.with_context(from_department=True).write({'department_ids': [(3, department.id)]})

        if 'division_ids' in vals and not self.env.context.get('from_division'):
            for branch in self:
                branch.division_ids.with_context(from_division=True).write({'department_id': branch.id})