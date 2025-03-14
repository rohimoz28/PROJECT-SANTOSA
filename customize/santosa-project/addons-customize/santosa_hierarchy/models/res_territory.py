from odoo import models, fields, api
from odoo.osv import expression

class ResTerritory(models.Model):
    _inherit = "res.territory"

    area_code = fields.Char('Area Code')
    branch_id = fields.Many2many("res.branch", string="Branch", domain="[('territory_id', '=', False)]")


    @api.depends('area_code','name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.area_code or ''} {account.name}"

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        if name:
            if str(name).find('-') != -1:
                user_ids = self._search(expression.AND([['|',('area_code', operator, str(str(name).split('-')[0]).replace(' ','')),('name',operator,name)], domain]), limit=limit, order=order)
                return user_ids
            else:
                user_ids = self._search(expression.AND([['|',('area_code', operator, name),('name',operator,name)], domain]), limit=limit, order=order)
                return user_ids

        else:
            return super()._name_search(name, domain, operator, limit, order)

    # @api.model
    # def create(self, vals):
    #     territory = super(ResTerritory, self).create(vals)
    #     if 'branch_id' in vals:
    #         for branch in territory.branch_id:
    #             branch.territory_id = territory
    #     return territory

    # def write(self, vals):
    #     res = super(ResTerritory, self).write(vals)
    #     if 'branch_id' in vals:
    #         for territory in self:
    #             territory.branch_id.write({'territory_id': territory.id})
    #     return res

    @api.model
    def create(self, vals):
        territory = super(ResTerritory, self).create(vals)
        if 'branch_id' in vals and not self.env.context.get('from_branch'):
            for branch in territory.branch_id:
                branch.with_context(from_territory=True).write({'territory_id': territory.id})
        return territory

    def write(self, vals):
        res = super(ResTerritory, self).write(vals)
        if 'branch_id' in vals and not self.env.context.get('from_branch'):
            for territory in self:
                territory.branch_id.with_context(from_territory=True).write({'territory_id': territory.id})
        return res