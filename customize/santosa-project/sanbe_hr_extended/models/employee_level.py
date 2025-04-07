from odoo import api, fields, models, _

class EmployeeLeveling(models.Model):
    _name = 'employee.level'
    _description = "Employee Level"
    _rec_name = 'name'

    name = fields.Char('Name')
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
               for node in arch.xpath("//field"):
                      node.set('readonly', 'True')
               for node in arch.xpath("//button"):
                      node.set('invisible', 'True')
        return arch, view
 