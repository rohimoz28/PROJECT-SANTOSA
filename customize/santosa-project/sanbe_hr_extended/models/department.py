from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Department(models.Model):
    _name = 'sanhrms.department'  # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Santosa Department Hierarchy'

    department_code = fields.Char('Department Code')
    name = fields.Char('Department Name')
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis')
    directorate_id = fields.Many2one(
        'sanhrms.directorate', string='Directorate')
    directorate_name = fields.Char(
        'Directorate Code', related='directorate_id.name', store=True)
    directorate_code = fields.Char(
        'Directorate Code', related='directorate_id.directorate_code', store=True)
    division_ids = fields.Many2many('sanhrms.division', string='Division')
    color = fields.Integer('Color Index')
    active = fields.Boolean('Active', default=True)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """
        Menambahkan kemampuan pencarian berdasarkan:
        - department_code
        - name
        - directorate_code
        - directorate_name
        """
        domain = domain or []
        if name:
            search_domain = [
                '|', '|','|',
                ('department_code', operator, name), ('directorate_name', operator, name),
                ('name', operator, name), ('directorate_code', operator, name)
            ]
            directorate_model = self.env['sanhrms.directorate']
            directorate_search_domain = [
                '|',
                ('directorate_code', operator, name),
                ('name', operator, name),
            ]
            directorate_ids = directorate_model._search(
                directorate_search_domain)

            if directorate_ids:
                search_domain = ['|'] + search_domain + \
                    [('directorate_id', 'in', directorate_ids)]
            full_domain = search_domain + domain
            return self._search(full_domain, limit=limit, order=order)
        return super(Department, self)._name_search(name, domain=domain, operator=operator, limit=limit, order=order)

    def write(self, vals):
        if 'active' in vals:
            new_active = vals.get('active')
            for record in self:
                if new_active and record.directorate_id and not record.directorate_id.active:
                    raise UserError(
                        "Cannot activate department because its directorate is inactive."
                    )
        res = super().write(vals)
        if 'active' in vals:
            for record in self:
                record.division_ids.sudo().write({'active': record.active})

        return res

    @api.depends('department_code', 'name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name}"
            account.display_name = '%s-%s' % (
                account.department_code or '', account.name)

    def unlink(self):
        return super(Department, self).unlink()

    # Saat buat record baru dan milih direktorat maka di direktorat nya akan terpilih department nya
    @api.model
    def create(self, vals):
        department = super(Department, self).create(vals)
        if 'directorate_id' in vals and not self.env.context.get('from_directorate'):
            department.directorate_id.with_context(from_directorate=True).write(
                {'department_ids': [(4, department.id)]})
        return department

    # def write(self, vals):
    #     old_directorate_map = {department.id: department.directorate_id for department in self}

    #     res = super(Department, self).write(vals)

    #     if 'directorate_id' in vals:
    #         for department in self:
    #             if department.directorate_id:
    #                 department.directorate_id.with_context(from_department=True).write({'department_ids': [(4, department.id)]})

    #             old_directorate = old_directorate_map.get(department.id)
    #             if old_directorate and old_directorate != department.directorate_id:
    #                 old_directorate.with_context(from_department=True).write({'department_ids': [(3, department.id)]})

    #     if 'division_ids' in vals and not self.env.context.get('from_division'):
    #         for branch in self:
    #             branch.division_ids.with_context(from_division=True).write({'department_id': branch.id})
