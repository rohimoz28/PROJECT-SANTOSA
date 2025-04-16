from odoo import fields, models, api

class SbTaxYearly (models.Model):
    _name = 'sb.tax.yearly'
    _description = 'Tax Yearly'

    tax_statutory_ids = fields.One2many('sb.tax.statutory', 'tax_yearly_id', string='Tax Statutory IDs')
    tax_fomula_ids = fields.One2many('sb.tax.formula', 'tax_yearly_id', string='Tax Fomula IDs')
    effective_date = fields.Date(string='Effective Date From')
    tk0 = fields.Float('TK0')
    tk1 = fields.Float('TK1')
    tk2 = fields.Float('TK2')
    tk3 = fields.Float('TK3')
    k0 = fields.Float('K0')
    k1 = fields.Float('K1')
    k2 = fields.Float('K2')
    k3 = fields.Float('K3')
    positional_allowance = fields.Float('Positional Allowance')
    or_max = fields.Float('Or Max')
    
    def unlink(self):
        return super(SbTaxYearly, self).unlink()

class SbTaxStatutory (models.Model):
    _name = 'sb.tax.statutory'
    _description = 'Tax Statutory'

    tax_yearly_id = fields.Many2one('sb.tax.yearly', string='Tax Yearly ID', ondelete='cascade')
    s_from = fields.Float('From')
    s_to = fields.Float('To')
    s_deduct = fields.Float('Deduct')

class SbTaxFormula (models.Model):
    _name = 'sb.tax.formula'
    _description = 'Tax Formula'

    tax_yearly_id = fields.Many2one('sb.tax.yearly', string='Tax Yearly ID', ondelete='cascade')
    f_from = fields.Float('From')
    f_to = fields.Float('To')
    f_factor_x = fields.Float('Faktor X')
    f_formula = fields.Text('Formula')
