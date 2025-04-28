from odoo import api, fields, models, _

class EmployeeLeveling(models.Model):
    _name = 'employee.level'
    _description = "Employee Level"
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active')
    branch_id = fields.Many2one('res.branch',string='Bisnis Unit')

#     def _get_view(self, view_id=None, view_type='form', **options):
#         arch, view = super()._get_view(view_id, view_type, **options)
#         if view_type in ('tree', 'form'):
#                for node in arch.xpath("//field"):
#                       node.set('readonly', 'True')
#                for node in arch.xpath("//button"):
#                       node.set('invisible', 'True')
#         return arch, view

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name + '(' + profesion.type.upper() + ')'
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(EmployeeLeveling, self).unlink()
