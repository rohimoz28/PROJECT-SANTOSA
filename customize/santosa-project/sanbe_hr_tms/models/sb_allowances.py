from odoo import fields, models, api
from odoo.exceptions import UserError


class SbAllowances(models.Model):
    _name = 'sb.allowances'
    _description = 'Master Table of Allowances'

    area_id = fields.Many2one('res.territory', string='Area')
    allowance_detail_ids = fields.One2many(
        comodel_name='sb.allowance.details',
        inverse_name='allowance_id',
        string='Attendance Allowance Deductions',
        required=False)

    @api.model
    def create(self, vals):
        # Check for duplicate area_id
        if self.search([('area_id', '=', vals['area_id'])]):
            raise UserError('Area already exists.')
        return super(SbAllowances, self).create(vals)
