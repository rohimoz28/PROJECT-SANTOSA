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
    
class EmpMstGroupUnitsService(models.Model):
    _name = 'mst.group.unit.pelayanan'
    _description = "Master Employee Group Unit Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', related='unit_name', store=True, tracking=True)
    branch_id = fields.Many2one('res.branch', 'Unit Bisnis', tracking=True)
    group_id = fields.Many2one('mst.group.pelayanan', 'Group', required=True, tracking=True)
    sub_group_id = fields.Many2one(
        'mst.sub.group.pelayanan',
        'Sub Group',
        domain="['|',('mst_id', '=', group_id),('mst_id', '=', False)]",
        required=True,
        tracking=True
    )
    group_unit_id = fields.Many2one('mst.group.unit', 'Unit', required=True, tracking=True)
    unit_name = fields.Char('Group Unit Detail', required=True, tracking=True)
    unit_from = fields.Integer()
    unit_to = fields.Integer()
    employee_id = fields.Many2one('hr.employee', 'Leader Group')
    employee_ids = fields.One2many('hr.employee','group_unit_id', string='Employee')
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.constrains('unit_from', 'unit_to')
    def _check_room_unit(self):
        for record in self:
            if record.unit_from and record.unit_to:
                if record.unit_to < record.unit_from:
                    raise UserError(_('Please set Start Unit lower than End Unit.'))

    _sql_constraints = [
        ('name_uniq', 'unique(unit_name, branch_id)', 'The unit name must be unique per branch!'),
        ('name_group_uniq', 'unique(unit_name, branch_id, group_id)', 'The unit name must be unique per group!'),
        ('name_sub_group_uniq', 'unique(unit_name, branch_id, group_id, sub_group_id)', 'The unit name must be unique per sub group!'),
        ('name_unit_uniq', 'unique(unit_name, branch_id, group_unit_id)', 'The unit name must be unique per unit!'),
    ]

    def unlink(self):
        return super().unlink()