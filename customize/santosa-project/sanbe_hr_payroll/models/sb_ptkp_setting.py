from odoo import api, fields, models, _
class SbPtkpSetting(models.Model):
    _name = 'sb.ptkp.setting'
    _description = "PTKP Setting"
    _rec_name = 'name'

    name = fields.Char(string='PTKP')
    ter_ids = fields.Many2many('sb.tax.setting', 'tax_setting_ptkp_setting_rel', string='TER')

    def unlink(self):
        return super(SbPtkpSetting, self).unlink()