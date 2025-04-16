from odoo import fields, models, api


class SbInsuranceSetting(models.Model):
    _name = 'sb.insurance.setting'
    _description = 'Insurance Setting'

    effective_date = fields.Date(string='Effective Date From')
    health_insurance = fields.Char('J. Kesehatan')
    hi_percentage = fields.Float('%')
    work_insurance = fields.Char('J. Keselamatan Kerja')
    wi_percentage = fields.Float('%')
    life_insurance = fields.Char('J. Kematian')
    li_percentage = fields.Float('%')
    retirement_insurance = fields.Char('J. Hari Tua')
    ri_percentage = fields.Float('%')
    employer_percentage = fields.Float('Employer')

    # name = fields.Char(string='Name', required=False)
    # code = fields.Char(string='Code', required=False)
    # percentage = fields.Float(string='Percentage', required=False)
    # effective_date = fields.Date(string='Effective Date', required=False)
    # taxpayer = fields.Selection(
    #     string='Taxpayer',
    #     selection=[('employee', 'Employee'),
    #                ('employer', 'Employer'), ],
    #     required=False, default='employee')

    # @api.constrains('name','effective_date','code')
    # def check_duplicate_record(self):
    #     for rec in self:
    #         '''Method to avoid duplicate overtime request'''
    #         duplicate_record = self.search([
    #             ('id', '!=', rec.id),
    #             ('name','=',rec.name),
    #             ('effective_date','=',rec.effective_date),
    #             ('code','=',rec.code),
    #         ])

    #         if duplicate_record:
    #             raise ValidationError(f"Duplicate record found for {rec.name}.")
