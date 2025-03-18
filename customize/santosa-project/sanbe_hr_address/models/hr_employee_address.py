from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class HrEmployeeAddresses(models.Model):
    _name = 'hr.employee.addresses'
    _description = 'List of Employee Addresses'

    employee_id = fields.Many2one('hr.employee', string='Employee ID', index=True)
    address_type = fields.Selection([
        ('KTP', 'KTP'),
        ('DOMISILI', 'Domisili'),
        ('MESS', 'Mess'),
        ('OTHER', 'Other')
    ], string='Address Type', required=True)
    address = fields.Text('Address')
    city = fields.Char('Kota/ Kab')
    district = fields.Char('Kecamatan')
    subdistrict = fields.Char('Kelurahan')
    rt = fields.Char('RT')
    rw = fields.Char('RW')
    default = fields.Boolean(string='Default', default=False)

    _sql_constraints = [
        ('unique_address_type', 'unique(employee_id, address_type)', 'Only one address per type allowed for an employee'),
    ]

    '''
        validation : one employee can not 
        have more than one default address
    '''
    @api.constrains('employee_id', 'default')
    def _check_unique_default_address(self):
        for record in self:
            if record.default:
                domain = [('employee_id', '=', record.employee_id.id), ('id', '!=', record.id), ('default', '=', True)]
                existing_default_address = self.search_count(domain)
                if existing_default_address:
                    raise UserError(_('Only one address can be default per employee'))
