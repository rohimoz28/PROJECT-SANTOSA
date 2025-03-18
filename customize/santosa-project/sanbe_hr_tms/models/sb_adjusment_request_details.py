from odoo import fields, models, api

REV_COMP_STATE = [
    ('ot1', 'Overtime - AOT1'),
    ('ot2', 'Overtime - AOT2'),
    ('ot3', 'Overtime - AOT3'),
    ('ot4', 'Overtime - AOT4'),
    ('day_attendee', 'Day Attendee'),
    ('unpaid_leave', 'Unpaid Leave'),
    ('maternity_leave', 'Maternity Leave'),
    ('permission', 'Permission'),
    ('salary_deduction', 'Salary Deduction'),
]

UOM_STATE = [
    ('days', 'Days'),
    ('hours', 'Hours'),
]

class SbAdjusmentRequestDetails(models.Model):
    _name = 'sb.adjusment.request.details'
    _description = 'Detail Adjusment Requests'

    adjusment_request_id = fields.Many2one(comodel_name='sb.adjustment.requests', string='Detail of Adjusment Request')
    revision_component = fields.Selection(string='Revision Component', selection=REV_COMP_STATE, required=False)
    start_qty = fields.Float(string='QTY Awal', required=False)
    start_uom = fields.Selection(string='Start UOM', selection=UOM_STATE, required=False)
    end_qty = fields.Float(string='QTY Akhir', required=False)
    end_uom = fields.Selection(string='End UOM', selection=UOM_STATE, required=False)
    variance = fields.Float(string='Variance', required=False)
    uom = fields.Float(string='UOM', required=False)
    code = fields.Char(string='Code', required=False)

