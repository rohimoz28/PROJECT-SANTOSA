from odoo import models, fields, api
from odoo.osv import expression

class ResBranch(models.Model):
    _inherit = "res.branch"

    branch_code = fields.Char('Branch Code')
    street = fields.Char(string='Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Char('State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country')
    territory_id = fields.Many2one('res.territory')
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')
    email = fields.Char('Email')
    unit_id = fields.Char(string='Kode Unit', required=False)
    directorate_ids = fields.Many2many("sanhrms.directorate", string="Directorate", domain="[('branch_id', '=', False)]")


    @api.depends('branch_code','name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = '%s - %s' %(account.branch_code or '', account.name)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        if name:
            if str(name).find('-') != -1:
                codenya = name.split('-')[0]
                namanya = name.split('-')[1]
                search_domain = ['|', ('branch_code', '=', str(codenya).replace(' ',"")), ('name', operator, str(namanya).replace(' ',""))]
                user_ids = self._search(search_domain, limit=limit, order=order)
                return user_ids
            else:
                search_domain = ['|',('branch_code', '=', name),('name',operator,name)]
                user_ids = self._search(search_domain, limit=limit, order=order)
                return user_ids
        else:
            return super()._name_search(name, domain, operator, limit, order)

    @api.model
    def create(self, vals):
        branch = super(ResBranch, self).create(vals)
        if 'territory_id' in vals and not self.env.context.get('from_territory'):
            branch.territory_id.with_context(from_branch=True).write({'branch_id': [(4, branch.id)]})
        return branch

    def write(self, vals):
        old_territory_map = {branch.id: branch.territory_id for branch in self}

        res = super(ResBranch, self).write(vals)

        if 'territory_id' in vals:
            for branch in self:
                if branch.territory_id:
                    branch.territory_id.with_context(from_branch=True).write({'branch_id': [(4, branch.id)]})
                
                old_territory = old_territory_map.get(branch.id)
                if old_territory and old_territory != branch.territory_id:
                    old_territory.with_context(from_branch=True).write({'branch_id': [(3, branch.id)]})

        if 'directorate_ids' in vals and not self.env.context.get('from_directorate'):
            for branch in self:
                branch.directorate_ids.with_context(from_directorate=True).write({'branch_id': branch.id})
        
        return res