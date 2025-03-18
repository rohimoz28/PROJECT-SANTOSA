# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _, Command


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.all_branch =[Command.set(allbranch.ids)]

    area = fields.Many2one('res.territory',string='Area',tracking=True,)
    all_branch = fields.Many2many('res.branch','res_users_rel',string='AllBranch',compute='_isi_semua_branch',store=False)
    branch_ids = fields.Many2many('res.branch',string="Allowed Branch",tracking=True)
    branch_id = fields.Many2one('res.branch', string='Branch', tracking=True, )




    def write(self, values):
        if 'branch_id' in values or 'branch_ids' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
        user = super(ResUsers, self).write(values)
        return user



