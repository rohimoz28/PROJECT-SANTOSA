from odoo import api, fields, models, _

class OpenPeriodeConfirmation(models.TransientModel):
    _name = 'wizard.open.periode.confirmation'
    _description = 'Wizard Konfirmasi Pembuatan Periode'

    data_values = fields.Serialized(string='Data Values')

    @api.model
    def default_get(self, fields_list):
        res = super(OpenPeriodeConfirmation, self).default_get(fields_list)
        context = self.env.context
        if context.get('default_data_values'):
            res['data_values'] = context['default_data_values']
        return res

    def process(self):
        vals = self.data_values
        if not vals:
            return {'type': 'ir.actions.act_window_close'}
        self.env['hr.tmsopenclose'].sudo().create([vals])
        return {'type': 'ir.actions.act_window_close'}