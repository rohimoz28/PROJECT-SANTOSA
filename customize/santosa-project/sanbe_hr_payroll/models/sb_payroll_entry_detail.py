from odoo import fields, models, api


class SbPayrollEntryDetail(models.Model):
    _name = 'sb.payroll.entry.detail'
    _description = 'Detail of Payroll Entry'

    master_id = fields.Many2one(comodel_name='sb.payroll.entry', string='Payroll Entry')
    pay_code = fields.Selection(
        string='Pay Code',
        selection=[('trans', 'TRANS'),
                   ('cash', 'CASH')],
        required=False)
    desc = fields.Text(string="Desc", required=False)
    type = fields.Char(
        string='Type',
        required=False)
    qty = fields.Float(
        string='Qty',
        required=False)
    amount = fields.Float(
        string='Amount',
        required=False)
    amount_total = fields.Float(
        string='Amount Total',
        required=False)
