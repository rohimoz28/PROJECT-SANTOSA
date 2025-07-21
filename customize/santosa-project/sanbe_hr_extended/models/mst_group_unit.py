from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class EmpGroupUnits(models.Model):
    _name = 'mst.group.unit'
    _description = "master Employee Group Unit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    name = fields.Char('Name',required=True,tracking=True)
    code = fields.Char('Code',required=True,size=6,tracking=True)
    active = fields.Boolean('Active',default=True,tracking=True)
    # branch_id = fields.Many2one('res.branch',string='Bisnis Unit',
    #   default=lambda self: self.env.user.branch_id,)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique!'),
        ('code_uniq', 'unique(code)', 'The code must be unique!'),
    ]

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(EmpGroupUnits, self).unlink()