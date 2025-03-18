from odoo import fields, models, api

EMP_PROFILE_STATE = [
    ('active', 'Active'),
    ('in_active', 'In Active'),
    ('hold', 'Hold')
]

EMP_GROUP1 = [
    ('Group1', 'Group 1 - Harian(pak Deni)'),
    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
    ('Group4', 'Group 4 - Security and non apoteker (bu Susi)'),
    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
    ('Group7', 'Group 7 - Tim Proyek (pak Ferry)'),
]

EMP_GROUP2 = [
    ('Group1', 'Group 1 - Harian(pak Deni)'),
    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
    ('Group4', 'Group 4 - security(bu Susi)'),
    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
]

class SbEmployeeProfile(models.Model):
    _name = 'sb.employee.profile'
    _description = 'Employee Profile'

    @api.model
    def _selection1(self):
        return EMP_GROUP1

    employee_group1 = fields.Selection(selection=_selection1, string='Employee P Group')
    employee_id = fields.Many2one('hr.employee', index=True)
    # employee_name = fields.Char(
    #     string='Employee Name',
    #     required=False)
    nik_new = fields.Char(
        string='NIK Baru',
        required=False)
    nik_old = fields.Char(
        string='NIK Lama',
        required=False)
    npwp = fields.Char(
        string='NPWP',
        required=False)
    gender = fields.Char(
        string='Gender',
        required=False)
    area_id = fields.Many2one('res.territory', string='Area', index=True)
    branch_id = fields.Many2one('res.branch', string='Business Unit', index=True)
    department_id = fields.Many2one('hr.department', string='Sub Department')
    job_id = fields.Many2one('hr.job',readonly=True, string="Job Position")
    job_status = fields.Char(string='Job Status',required=False)
    employement_status = fields.Char(string='Employement Status', required=False)
    state = fields.Selection(string='State', selection=EMP_PROFILE_STATE, default='active')
    # employement details
    pay_type = fields.Selection(
        string='Pay Type',
        selection=[('monthly', 'Monthly'),
                   ('daily', 'Daily'), ],
        required=False)
    pay_period = fields.Selection(
        string='Pay Period',
        selection=[('monthly', 'Monthly'),
                   ('daily', 'Daily'), ],
        required=False)
    effective_date = fields.Date(
        string='Effective Date',
        required=False)
    bank_account = fields.Char(
        string='Bank Account',
        required=False)
    basic_salary = fields.Float(
        string='Basic Salary',
        required=False)
    status_ptkp = fields.Selection(
        string='Status PTKP',
        selection=[('tk0', 'TKO'),
                   ('tk1', 'TK1')],
        required=False)
    type_ter = fields.Selection(
        string='Type TER',
        selection=[('tera', 'TER A'),
                   ('terb', 'TER B')],
        required=False)
    bpjs_no = fields.Char(
        string='BPJS No',
        required=False)
    jamsostek_no = fields.Char(
        string='Jamsostek No',
        required=False)
    # end employement details
    compensation_ids = fields.One2many(
        comodel_name='sb.compensation',
        inverse_name='compensation_id',
        string='Compensation Details',
        required=False)

    @api.onchange('employee_id')
    def employee_onchange(self):
        for rec in self:
            if rec.employee_id:
                emp = self.env['hr.employee'].sudo().search([('id','=',rec.employee_id.id)],limit=1)
                if emp:
                    rec.nik_new = emp.nik
                    rec.nik_old = emp.nik_lama
                    rec.department_id = emp.department_id
                    rec.job_id = emp.job_id
                    rec.employement_status = emp.emp_status
                    rec.job_status = emp.job_status
                    rec.gender = emp.gender
                    rec.area_id = emp.area
                    rec.branch_id = emp.branch_id

    # Override the create method to persist data when a new record is created
    @api.model
    def create(self, vals):
        record = super(SbEmployeeProfile, self).create(vals)
        if record.employee_id:
            emp = self.env['hr.employee'].sudo().search([('id', '=', record.employee_id.id)], limit=1)
            if emp:
                record.sudo().write({
                    'nik_new': emp.nik,
                    'nik_old': emp.nik_lama,
                    'department_id': emp.department_id.id,
                    'job_id': emp.job_id.id,
                    'employement_status': emp.emp_status,
                    'job_status': emp.job_status,
                    'gender': emp.gender,
                    'area_id': emp.area.id,
                    'branch_id': emp.branch_id.id
                })
        return record

    def action_view_employee_profile_details(self):
        pass
        # return {
        #     'name': 'action_view_tms_details',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'sb.tms.tmsentry.details',
        #     # 'views': [(False, 'form')],
        #     # 'view_id': False,
        #     'view_id': self.env.ref('sanbe_hr_tms.tmsentry_details_form_view').id,
        #     'target': 'new',
        #     'res_id': self.id,
        #     'context': False,
        # }