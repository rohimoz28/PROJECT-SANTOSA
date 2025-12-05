from odoo import models, fields, api


class Directorate(models.Model):
    _name = 'sanhrms.directorate'  # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Santosa Directorate Hierarchy'

    directorate_code = fields.Char('Directorate Code')
    name = fields.Char('Directorate Name')
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis')
    department_ids = fields.Many2many(
        "sanhrms.department", string="Department")
    active = fields.Boolean('Active', default=True)
    color = fields.Integer('Color Index')
    # state_active = fields.Boolean('Active', default=True)

    @api.depends('directorate_code', 'name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name}"
            account.display_name = '%s-%s' % (
                account.directorate_code or '', account.name)

    def unlink(self):
        return super(Directorate, self).unlink()

    # @api.onchange("state_active")
    # def _bypass_active_change(self):
    #     for line in self:
    #         line.write({'active': line.state_active})

    @api.model
    def create(self, vals):
        directorate = super(Directorate, self).create(vals)
        if 'branch_id' in vals and not self.env.context.get('from_branch'):
            directorate.branch_id.with_context(from_directorate=True).write(
                {'directorate_ids': [(4, directorate.id)]})
        return directorate

    def write(self, vals):
        old_branch_map = {
            directorate.id: directorate.branch_id for directorate in self}

        res = super(Directorate, self).write(vals)

        if 'branch_id' in vals:
            for directorate in self:
                if directorate.branch_id:
                    directorate.branch_id.with_context(from_directorate=True).write(
                        {'directorate_ids': [(4, directorate.id)]})

                old_branch = old_branch_map.get(directorate.id)
                if old_branch and old_branch != directorate.branch_id:
                    old_branch.with_context(from_directorate=True).write(
                        {'directorate_ids': [(3, directorate.id)]})

        if 'department_ids' in vals and not self.env.context.get('from_department'):
            for branch in self:
                branch.department_ids.with_context(from_department=True).write({
                    'directorate_id': branch.id})

    def write(self, vals):
        if 'active' in vals:
            new_active = vals.get('active')
        res = super().write(vals)
        if 'active' in vals:
            for record in self:
                record.department_ids.write({'active': record.active})
        return res
