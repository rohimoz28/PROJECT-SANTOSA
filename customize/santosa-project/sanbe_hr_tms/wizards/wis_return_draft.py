from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class HrStateSetDraft(models.TransientModel):
    _name = 'wiz.hr.set.draft'
    _description = 'HR Set Draft Wizard'
    target_models = fields.Selection([
        ('hr.employee', 'Employee'),
        ('sb.employee.shift', 'Employee Shift'),
    ], string='Target Model', required=True, help="Select the model to set records to draft.")
    shift_id = fields.Many2one(
        'sb.employee.shift', string='Employee Shifts', help="Select shifts to set to draft.")
    reason = fields.Char(
        string='Reason',
        required=True,
        help='Reason for setting the record to draft.'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(HrStateSetDraft, self).default_get(fields_list)
        if 'reason' in fields_list:
            res['reason'] = False
        if 'shift_ids' in fields_list:
            active_shifts = self.env['sb.employee.shift'].search(
                [('state', '=', 'active')])
            res['shift_ids'] = active_shifts.ids

        return res

    def action_set_draft(self):
        if not self.reason:
            raise ValidationError(
                _('Please provide a reason for setting the records to draft.'))
        if self.target_models == 'sb.employee.shift':
            for shift in self.shift_id:
                if shift.state != 'draft':
                    _logger.info("Setting shift %s to draft", shift.id)
                    shift.write({'state': 'draft', 'reason': self.reason, 'approved_by': False,
                                'approved_date': False, 'review_by': False, 'review_date': False})
        elif self.target_models == 'hr.employee':
            _logger.info("Setting employees to draft (example)")
        return {'type': 'ir.actions.act_window_close'}
