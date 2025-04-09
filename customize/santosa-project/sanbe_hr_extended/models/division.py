from odoo import models, fields, api

class Division(models.Model):
    _name = 'sanhrms.division' # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Division Hierarchy'

    division_code = fields.Char('Division Code')
    name = fields.Char('Division Name')
    branch_id = fields.Many2one('res.branch',string='Bisnis Unit')
    department_id = fields.Many2one('sanhrms.department',string='Department')
    active = fields.Boolean('Active', default=True )

    # @api.depends('department_code','name')
    # def _compute_display_name(self):
    #     for account in self:
    #         account.display_name = f"{account.name}"
            # account.display_name = '%s-%s' % (account.department_code   or '', account.name)

    @api.model
    def create(self, vals):
        division = super(Division, self).create(vals)
        if 'department_id' in vals and not self.env.context.get('from_department'):
            division.department_id.with_context(from_department=True).write({'division_ids': [(4, division.id)]})
        return division

    def write(self, vals):
        old_department_map = {division.id: division.department_id for division in self}

        res = super(Division, self).write(vals)

        if 'department_id' in vals:
            for division in self:
                if division.department_id:
                    division.department_id.with_context(from_division=True).write({'division_ids': [(4, division.id)]})
                
                old_department = old_department_map.get(division.id)
                if old_department and old_department != division.department_id:
                    old_department.with_context(from_division=True).write({'division_ids': [(3, division.id)]})