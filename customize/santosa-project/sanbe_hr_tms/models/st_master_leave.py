from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError


class StMasterLeave(models.Model):
    _name = 'st.master.leave'
    _description = 'Master Table of Leaves'

    area_id = fields.Many2one(comodel_name='res.territory', string='Area')
    branch_ids = fields.Many2many(
        comodel_name = "res.branch",
        relation = "res_branch_rel",
        string = "All Branches",
        compute = "_isi_semua_branch",
        store = False
    )
    branch_id = fields.Many2one(
        comodel_name = "res.branch",
        string = "Unit Bisnis",
        domain = "[('id','in',branch_ids)]"
    )
    name = fields.Char(string='Nama cuti')
    code = fields.Char(string='Kode cuti')
    day = fields.Integer(string='Jumlah Hari')


    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]


    @api.constrains('code')
    def duplicate_code_check(self):
        for rec in self:
            duplicate_code = self.search([
                ('id', '!=', rec.id),
                ('code','=',rec.code),
            ])
            if duplicate_code:
                raise ValidationError(f"Ditemukan Kode Duplikat: {rec.code}.")
