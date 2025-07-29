from odoo import fields, models, api
from datetime import date


class hrPensionMonitoring(models.Model):
    _inherit='hr.employee'


    pension_date = fields.Date('Pension Date')

    pension_state = fields.Selection(
        selection=[
            ('expired','Expired'),
            ('running','Running'),
        ],
        string="Status Pensiun", compute="_pension_state_compute", store=False
    )

    @api.depends('pension_date')
    def _pension_state_compute(self):
        for rec in self:
            if rec.pension_date:
                if date.today() < rec.pension_date:
                    rec.pension_state = 'running'
                else:
                    rec.pension_state = 'expired'
            else:
                rec.pension_state = False