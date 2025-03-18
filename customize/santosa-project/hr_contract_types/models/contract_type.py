# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    sequence = fields.Integer()
    country_id = fields.Many2one('res.country')

    @api.depends('name')
    def _compute_code(self):
        for contract_type in self:
            if contract_type.code:
                continue
            contract_type.code = contract_type.name


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
