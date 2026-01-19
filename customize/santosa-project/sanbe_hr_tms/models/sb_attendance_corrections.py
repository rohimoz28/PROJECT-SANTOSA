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
                mybranch = self.env['res.branch'].search(
                    [('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search(
                [('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    def _get_running_periode(self):
        """Mendapatkan periode 'running' yang aktif untuk Branch pengguna saat ini."""
        user_branch_id = self.env.user.branch_id.id
        if not user_branch_id:
            return False

        return self.env['hr.opening.closing'].search([
            ('state_process', '=', 'running'),
            ('branch_id', '=', user_branch_id),
            ('open_periode_from', '<=', fields.Datetime.now()),
            ('open_periode_to', '>=', fields.Datetime.now())
        ], order='id desc', limit=1)

    period_id = fields.Many2one(
        'hr.opening.closing',
        string='Period',
        index=True,
        default=_get_running_periode,
        domain="[('state_process','in',('draft','running'))]"
    )

    # def _generate_name(self):
    #     user_periode = self.period_id.id
    #     if not user_periode:
    #         return False
    #     return f"{self.period_id.name}-{self.id:04d}"

    # name = fields.Char(string='Name', compute="_generate_name",
    #                    readonly=True, copy=False, index=True)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel',
                                  string='AllBranch', compute='_isi_semua_branch', store=False)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True, domain="[('id','in',branch_ids)]",
                                readonly="state =='done'", default=lambda self: self.env.user.branch_id.id)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    division_id = fields.Many2one(
        'sanhrms.division', string='Divisi', store=True, readonly="state =='done'")
    hrms_department_id = fields.Many2one(
        'sanhrms.department', string='Departemen', store=True, readonly="state =='done'")
    directorate_id = fields.Many2one(
        'sanhrms.directorate', string='Direktorat', store=True, readonly="state =='done'")
    attn_correction_detail_ids = fields.One2many(
        comodel_name='sb.attendance.correction.details',
        inverse_name='attn_correction_id',
        string='Attendance Correction Details',
        required=False)
    attn_loss_detail_ids = fields.One2many(
        comodel_name='sb.loss.attendance.details',
        inverse_name='attn_correction_id',
        string='Attendance Incomplete Details',
        required=False)
