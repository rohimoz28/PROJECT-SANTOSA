from odoo import api, fields, models, _

class EmployeeLeveling(models.Model):
    _name = 'employee.level'
    _description = "Employee Level"
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active',default=True)
    # branch_id = fields.Many2one('res.branch',string='Bisnis Unit',
    #   default=lambda self: self.env.user.branch_id,)

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for profesion in self:
            name = ''
            if profesion.code and profesion.name:
                name = '[' +  profesion.code +'] ' + profesion.name
            profesion.display_name = name

    # @api.model
    def unlink(self):
        return super(EmployeeLeveling, self).unlink()
