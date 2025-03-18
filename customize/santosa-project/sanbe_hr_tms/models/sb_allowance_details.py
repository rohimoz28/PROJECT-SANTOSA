from odoo import fields, models, api


class SbAllowanceDetails(models.Model):
    _name = 'sb.allowance.details'
    _description = 'Detail Table of Allowances'

    # name = fields.Char()
    allowance_id = fields.Many2one(comodel_name='sb.allowances', string='Allowance Deduction Details')
    code = fields.Selection([('ashf','ASHF - Attendee Premi'),
                             ('ans1','ANS1 - Night Shift Allowance 1'),
                             ('ans2','ANS2 - Night Shift Allowance 2'),
                             ('atrp','ATRP - Transport Allowance'),
                             ('amea','AMEA - Meal Allowance')],default='ashf',string='Component Code')
    time_from = fields.Float('Time From')
    time_to = fields.Float('Time To')
    qty = fields.Float('Qty')

