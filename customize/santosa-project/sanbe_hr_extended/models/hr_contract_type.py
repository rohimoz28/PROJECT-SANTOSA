from odoo import fields, models


class hrContractTypeInherit(models.Model):
    _inherit = 'hr.contract.type'

    is_active = fields.Boolean(string="Active")