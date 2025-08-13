from email.policy import default

from odoo import fields, models, api, _, Command
from datetime import datetime

ADJ_REQ_STATE = [
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('closed', 'Closed')
]

class SbAdjusmentRequests(models.Model):
    _name = 'sb.adjustment.requests'
    _description = 'Master Adjusment Requests'

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area_id', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id', '=', allrecs.branch_id.id),('active','=',True)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]

    name = fields.Char(string='Transaction Number')
    area_id = fields.Many2one('res.territory', index=True, string='Area')
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch')
    branch_id = fields.Many2one('res.branch',
        string='Business Unit',
        index=True,
        domain="[('id','in',branch_ids)]")
    request_no = fields.Integer(string='Request Number',required=False)
    request_date = fields.Date(string='Request Date', required=False)
    alldepartment = fields.Many2many('hr.department','hr_employeelist_schedule_rel', string='All Department',compute='_isi_department_branch',store=False)
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', related='employee_id.directorate_id', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', 
                                         related='employee_id.hrms_department_id', store=True)
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    aplicant = fields.Selection(
        string='Applicant',
        selection=[('employee', 'Employee'),
                   ('personalia', 'Personalia'), ],
        required=False, default='employee',)

    state = fields.Selection(string='Status', selection=ADJ_REQ_STATE, required=False, default='draft')
    revision_period_from = fields.Date(string='Revision Period From', required=False)
    revision_period_to = fields.Date(string='Revision Period To', required=False)
    trx_date = fields.Date(string='Transaction Date', required=False, default=datetime.today())
    manager_approved = fields.Boolean(
        string='Manager Approved',
        required=False)
    plant_manager_approved = fields.Boolean(
        string='Plant Manager Approved',
        required=False)
    hrd_approved = fields.Boolean(
        string='HRD Approved',
        required=False)
    sb_adjument_request_ids = fields.One2many(
        comodel_name='sb.adjusment.request.details',
        inverse_name='adjusment_request_id',
        string='Adjusment Request Details',
        required=False)
    chronology = fields.Text(string="Chronology", required=False)

    @api.model
    def create(self, vals):
        # Get the last record to determine the next number
        last_record = self.search([], order='id desc', limit=1)
        next_number = last_record.id + 1 if last_record else 1

        # Format the running number with leading zeros
        vals['name'] = str(next_number).zfill(6)

        return super(SbAdjusmentRequests, self).create(vals)

    def btn_send_to_fin(self):
        for rec in self:
            rec.state = 'closed'

    def btn_approve(self):
        for rec in self:
            rec.state = 'approved'

    def btn_reject(self):
        for rec in self:
            rec.state = 'rejected'

