from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class Division(models.Model):
    _name = 'sanhrms.division'  # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Division Hierarchy'

    division_code = fields.Char('Division Code')
    name = fields.Char('Division Name')
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis')
    department_id = fields.Many2one(
        'sanhrms.department', string='Department', required=True)
    department_name = fields.Char(
        related='department_id.name', string='Department', required=True)
    department_code = fields.Char(
        'Department Code', related='department_id.department_code', store=True)
    active = fields.Boolean('Active', default=True)
    # state_active = fields.Boolean('Active', default=True)
    color = fields.Integer('Color Index')
    employee_ids = fields.One2many(
        'hr.employee', 'division_id', string='Employees')

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if not name:
            return super(Division, self)._name_search(name, domain=domain, operator=operator, limit=limit, order=order)
        search_domain = [
            '|', '|', '|',
            ('division_code', operator, name),
            ('name', operator, name), ('department_code', operator,
                                       name), ('department_name', operator,
                                               name)
        ]
        search_domain.append(('department_code', operator, name))
        department_model = self.env['sanhrms.department']
        department_search_domain = [
            '|',
            ('department_code', operator, name),
            ('name', operator, name),
        ]
        department_ids = department_model._search(department_search_domain)
        if department_ids:
            search_domain = ['|'] + search_domain + \
                [('department_id', 'in', department_ids)]
        full_domain = search_domain + domain
        return self._search(full_domain, limit=limit, order=order)

    @api.depends('division_code', 'name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name}"
            account.display_name = '%s-%s' % (
                account.division_code or '', account.name)

    def unlink(self):
        return super(Division, self).unlink()

    @api.model
    def create(self, vals):
        division = super(Division, self).create(vals)
        if 'department_id' in vals and not self.env.context.get('from_department'):
            division.department_id.with_context(from_department=True).write(
                {'division_ids': [(4, division.id)]})
        return division

    # def write(self, vals):
    #     old_department_map = {
    #         division.id: division.department_id for division in self}

    #     res = super(Division, self).write(vals)

    #     if 'department_id' in vals:
    #         for division in self:
    #             if division.department_id:
    #                 division.department_id.with_context(from_division=True).write(
    #                     {'division_ids': [(4, division.id)]})

    #             old_department = old_department_map.get(division.id)
    #             if old_department and old_department != division.department_id:
    #                 old_department.with_context(from_division=True).write(
    #                     {'division_ids': [(3, division.id)]})

    def write(self, vals):
        if 'active' in vals:
            new_active = vals.get('active')
            for record in self:
                if new_active and record.department_id and not record.department_id.active:
                    raise UserError(
                        "Cannot activate division because its department is inactive."
                    )
        res = super().write(vals)
        return res
