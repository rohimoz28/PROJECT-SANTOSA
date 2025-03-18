# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

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
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')
    email = fields.Char('Email')
    unit_id = fields.Char(string='Kode Unit', required=False)

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