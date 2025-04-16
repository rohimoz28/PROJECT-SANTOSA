from odoo import fields, models, api

class SbTaxSetting (models.Model):
    _name = 'sb.tax.setting'
    _description = 'Tax Setting'
    _rec_name = 'ter_names'

    ts_details_ids = fields.One2many('sb.tax.setting.details', 'tax_setting_id', string='Tax Setting Details IDs')
    # ter_name = fields.Selection([
    #                             ('TER_A', 'TER A'),
    #                             ('TER_B', 'TER B'),
    #                             ('TER_C', 'TER C')
    #                             ], string='TER Name')
    ter_names = fields.Char('TER Name')
    ed_from = fields.Date('Effective Date From')
    # ptkp = fields.Selection([
    #                         ('TK/0', 'TK/0'),
    #                         ('TK/1', 'TK/1'),
    #                         ('TK/2', 'TK/2'),
    #                         ('TK/3', 'TK/3'),
    #                         ('K/0', 'K/0'),
    #                         ('K/1', 'K/1'),
    #                         ('K/2', 'K/2'),
    #                         ('K/3', 'K/3'),
    #                         ], string='PTKP')
    ptkp_ids = fields.Many2many('sb.ptkp.setting', 'tax_setting_ptkp_setting_rel', string='PTKP')
    status = fields.Char('Status')

    def unlink(self):
        return super(SbTaxSetting, self).unlink()

class SbTaxSettingDetails (models.Model):
    _name = 'sb.tax.setting.details'
    _description = 'Tax Setting.details'

    tax_setting_id = fields.Many2one('sb.tax.setting', string='Tax Setting ID', ondelete='cascade')
    bruto_from = fields.Float('Bruto From')
    bruto_to = fields.Float('Bruto To')
    percent = fields.Float('%')