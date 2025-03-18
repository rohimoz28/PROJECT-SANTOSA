from odoo import fields, models, api


class SbCompensation(models.Model):
    _name = 'sb.compensation'
    _description = 'Employee Compensation'

    compensation_id = fields.Many2one(comodel_name='sb.employee.profile', string='Compensation')
    pay_code = fields.Selection(
        string='Pay Code',
        selection=[('trans', 'TRANS'),
                   ('cash', 'CASH')],
        required=False)
    type = fields.Char(
        string='Type',
        required=False)
    amount = fields.Float(
        string='Amount',
        required=False)
    remarks = fields.Text(
        string="Remarks",
        required=False)
    is_tax = fields.Boolean(
        string='Tax',
        required=False)
    formula = fields.Char(
        string='Formula',
        required=False)
