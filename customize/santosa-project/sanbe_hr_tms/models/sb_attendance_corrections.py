from odoo import fields, models, api
class SbAttendanceCorrections (models.Model):
    _name = 'sb.attendance.corrections'
    _description = 'Attendance Corrections Header'

    # Function For Filter Branch in Area
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    period_id = fields.Many2one('hr.opening.closing', string='Periode', index=True)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True, domain="[('id','in',branch_ids)]",
                                readonly="state =='done'")
    department_id = fields.Many2one('hr.department', string='Sub Department')
    attn_correction_detail_ids = fields.One2many(
        comodel_name='sb.attendance.correction.details',
        inverse_name='attn_correction_id',
        string='Attendance Correction Details',
        required=False)
