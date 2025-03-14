from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

class HREmployeeAssets(models.Model):
    _name = "hr.employee.assets"

    employee_id = fields.Many2one('hr.employee',string='Employee ID',index=True)
    asset_name = fields.Char('Asset/Benefit Type')
    asset_number = fields.Char('Asset/Benefit Number')
    uom = fields.Many2one('uom.uom',string='UOM')
    asset_qty = fields.Float('QTY')
    keterangan = fields.Text('Keterangan')

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