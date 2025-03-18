# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api
from odoo.osv import expression

class ResTerritory(models.Model):
    _inherit = "res.territory"

    area_code = fields.Char('Area Code')

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