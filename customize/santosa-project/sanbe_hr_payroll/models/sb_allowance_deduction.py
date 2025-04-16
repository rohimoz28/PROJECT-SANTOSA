from odoo import fields, models, api

class SbAllowanceDeduction (models.Model):
    _name = 'sb.allowance.deduction'
    _description = 'Allowance Deduction'

    ed_from = fields.Date('Effective Date From')
    state  = fields.Selection([
                              ('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('inactive', 'Inactive')
                              ], string='Status', default='draft')
    pay_code = fields.Char('Pay Code')
    desc = fields.Text('Description')
    pay_type = fields.Selection([
                                ('by_formula', 'By Formula'),
                                ('fixed_amount', 'Fixed Amount'),
                                ('amt_time', 'Fix Amt and Times'),
                                ], string='Pay Type')
    pay_group = fields.Selection([
                                ('allowance', 'Allowance'),
                                ('overtime', 'Overtime'),
                                ('deduction', 'Deduction'),
                                ('bonus', 'Bonus'),
                                ], string='Pay Group')
    formula = fields.Text('Formula')
    fixed_amount = fields.Float('Fixed Amount')
    times = fields.Float('Times')
    remarks = fields.Char('Remarks')
    isTaxable = fields.Boolean('Taxable')

    def btn_draft(self):
        for rec in self:
            rec.state = 'draft'

    def btn_approve(self):
        for rec in self:
            rec.state = 'approved'
    
    def btn_inactive(self):
        for rec in self:
            rec.state = 'inactive'

