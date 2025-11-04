
from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError

OT_HOURS_SELECTION = [
    ('h_morning', "H - Lembur Pagi : 07.00 - 15.00"),
    ('h_afternoon', "H - Lembur Siang : 15.00 - 22.00"),
    ('h_night', "H - Lembur Malam  : 22.00 - 06.00"),
    ('r_s1', "R - S1 : 15.30 - 19.30"),
    ('r_s2', "R - S2 : 11.00 - 15.00"),
    ('r_s3', "R - S3 : 19.00 - 22.00"),
    ('others', "Others"),
]


class HrCariEmployeeDepartment(models.TransientModel):
    _name = 'hr.employeedepartment'
    _description = 'Search Employee Department Wizard'

    # name = fields.Char(string="Name")
    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
    branch_id = fields.Many2one('res.branch', string='Bisnis Unit', index=True, domain="[('id','in',branch_ids)]")
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department')
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', store=True)
    empgroup_id = fields.Many2one('hr.empgroup', string='Employee Group Setting')
    plan_id = fields.Many2one('hr.overtime.planning', string='Planning OT', index=True)
    plann_date_from = fields.Date('Tanggal SPL',default=fields.Date.today(),)
    plann_date_to = fields.Date('Plann Date To',default=fields.Date.today(),)
    ot_plann_from = fields.Float('Jam SPL Dari',)
    ot_plann_to = fields.Float('Jam SPL Hingga')
    approve_time_from = fields.Float('Approve Time From')
    approve_time_to = fields.Float('Approve Time To')
    machine = fields.Char('Machine')
    work_plann = fields.Char('Rencana SPL')
    output_plann = fields.Char('Output SPL')
    transport = fields.Boolean('Transport')
    meals = fields.Boolean('Meal')
    valid_from = fields.Date('Valid From', copy=True,default=fields.Date.today(),)
    valid_to = fields.Date('To', copy=True,default=fields.Date.today(),)
    wdcode = fields.Many2one(
        'hr.working.days',
        domain="[('id','in',wdcode_ids)]",
        string='WD Code',
        copy=True,
        index=True
    )
    branch_ids = fields.Many2many(
        'res.branch', 'res_branch_plan_ot_rel',
        string='AllBranch',
        compute='_isi_semua_branch',
        store=False
    )
    alldepartment = fields.Many2many(
        'sanhrms.department',
        'hr_department_plan_ot_rel',
        string='All Department',
        compute='_isi_department_branch',
        store=False
    )
    employee_ids = fields.One2many(
        'hr.employeedepartment.details',
        'cari_id',
        auto_join=True,
        string='Cari Employee Details'
    )
    modelname = fields.Selection([
        ('hr.empgroup', 'hr.empgroup'),
        ('hr.overtime.planning', 'hr.overtime.planning')
    ])
    wdcode_ids = fields.Many2many(
        'hr.working.days', 'wd_plan_ot_rel',
        string='WD Code All',
        copy=True,
        compute='_isi_department_branch',
        store=False
    )
    default_ot_hours = fields.Selection(
        selection=OT_HOURS_SELECTION,
        string='Default Jam OT',store=True)
    # @api.models(self,vals)
    # def create(self)

    @api.onchange('default_ot_hours')
    def onchange_default_ot_hours(self):
        if self.default_ot_hours == 'h_morning':
            self.ot_plann_from = 7.0
            self.ot_plann_to = 15.0
        elif self.default_ot_hours == 'h_afternoon':
            self.ot_plann_from = 15.0
            self.ot_plann_to = 22.0
        elif self.default_ot_hours == 'h_night':
            self.ot_plann_from = 22.0
            self.ot_plann_to = 6.0
        elif self.default_ot_hours == 'r_s1':
            self.ot_plann_from = 15.5
            self.ot_plann_to = 19.5
        elif self.default_ot_hours == 'r_s2':
            self.ot_plann_from = 11.0
            self.ot_plann_to = 15.0
        elif self.default_ot_hours == 'r_s3':
            self.ot_plann_from = 19.0
            self.ot_plann_to = 22.0
        else:
            self.ot_plann_from = 0.0
            self.ot_plann_to = 0.0

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            # Get all branch names in one go and search branches in a single query
            branch_ids = allrecs.area_id.branch_id.ids
            if branch_ids:
                allbranch = self.env['res.branch'].sudo().search([('id', 'in', branch_ids)])
                allrecs.branch_ids = [Command.set(allbranch.ids)]
            else:
                allrecs.branch_ids = [Command.clear()]

    @api.depends('area_id', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            if allrecs.branch_id:
                # Get all departments in a single query
                allbranch = self.env['sanhrms.department'].sudo().search(['|',('branch_id', '=', allrecs.branch_id.id),('branch_id', '=', False)])
                allrecs.alldepartment = [Command.set(allbranch.ids)]
            else:
                allrecs.alldepartment = [Command.clear()]

            # Fetch working days efficiently in one go
            allwds = self.env['hr.working.days'].sudo().search([
                ('area_id', '=', allrecs.area_id.id),
                ('available_for', 'in', [allrecs.branch_id.id] if allrecs.branch_id else []),
                ('is_active', '=', True)
            ])
            allrecs.wdcode_ids = [Command.set(allwds.ids)]

    @api.model
    def default_get(self, fields):
        result = super(HrCariEmployeeDepartment, self).default_get(fields)
        myempg = self._context.get('active_id')
        fieldname = self._context.get('fieldname', 'empgroup_id')  # Simplified logic
        if myempg:
            result[fieldname] = myempg
        return result

    def _get_filtered_employees_domain(self):
        """
        Build domain to filter employees based on selected fields.
        """
        domain = [('state', '=', 'approved'),('emp_status_id', '!=', False)]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        # if self.department_id:
        #     domain.append(('department_id', '=', self.department_id.id))
        if self.hrms_department_id:
            domain.append(('hrms_department_id', '=', self.hrms_department_id.id))
        if self.directorate_id:
            domain.append(('directorate_id', '=', self.directorate_id.id))
        if self.division_id:
            domain.append(('division_id', '=', self.division_id.id))
        return domain

    def _isi_employee(self):
        for rec in self:
            rec.employee_ids = [(5, 0, 0)]
            domain = rec._get_filtered_employees_domain()
            employees = self.env['hr.employee'].search(domain)
            datadetails = self.env['hr.employeedepartment.details']
            if employees:
                for emp in employees:
                    datadetails.sudo().create({
                        'cari_id': rec.id,
                        'employee_id': emp.id,
                        'department_id': emp.department_id.id,
                        'nik': emp.nik,
                        'job_id': emp.job_id.id,
                        'hrms_department_id': emp.hrms_department_id.id,
                        'directorate_id': emp.directorate_id.id,
                        'division_id': emp.division_id.id,
                        'is_selected': False,
                    })

    def action_insert_empgroup(self):
        context_field = self._context.get('fieldname')
        employee_data = []

        if self.modelname == 'hr.overtime.planning':
            for emp in self.employee_ids.filtered(lambda e: e.is_selected):
                employee_data.append({
                    'planning_id': self.plan_id.id,
                    'area_id': emp.employee_id.area.id,
                    'branch_id': emp.employee_id.branch_id.id,
                    'department_id': emp.employee_id.department_id.id,
                    'division_id': emp.employee_id.division_id.id,
                    'hrms_department_id': emp.employee_id.hrms_department_id.id,
                    'directorate_id': emp.employee_id.directorate_id.id,
                    'employee_id': emp.employee_id.id,
                    'nik': emp.employee_id.nik,
                    'plann_date_from': self.plann_date_from,
                    'plann_date_to': self.plann_date_to,
                    'ot_plann_from': self.ot_plann_from,
                    'ot_plann_to': self.ot_plann_to,
                    'machine': self.machine,
                    'work_plann': self.work_plann,
                    'output_plann': self.output_plann,
                    'transport': self.transport,
                    'meals': self.meals,
                    'ot_type': 'regular',
                    'approve_time_from': self.approve_time_from,
                    'approve_time_to': self.approve_time_to,
                })
            self.env['hr.overtime.employees'].sudo().create(employee_data)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.overtime.planning',
                'view_mode': 'form',
                'target': 'current',
                'res_id': self.plan_id.id,
                'views': [[False, 'form']],
            }
        else:
            # Ensure required fields are set
            if not self.wdcode and self.modelname != 'hr.overtime.planning':
                raise UserError('WD Code must be selected.')
            if not self.valid_from and self.modelname != 'hr.overtime.planning':
                raise UserError('Date Valid From must be selected.')
            if not self.valid_to  and self.modelname != 'hr.overtime.planning':
                raise UserError('Date Valid To must be selected.')

            # Processing for other contexts
            for emp in self.employee_ids.filtered(lambda e: e.is_selected):
                employee_data.append({
                    'empgroup_id': self.empgroup_id.id,
                    'area_id': emp.employee_id.area.id,
                    'branch_id': emp.employee_id.branch_id.id,
                    'department_id': emp.department_id.id,
                    'division_id': emp.division_id.id,
                    'hrms_department_id': emp.hrms_department_id.id,
                    'directorate_id': emp.directorate_id.id,
                    'employee_id': emp.employee_id.id,
                    'nik': emp.employee_id.nik,
                    'job_id': emp.job_id.id,
                    'wdcode': self.wdcode.id,
                    'valid_from': self.valid_from,
                    'valid_to': self.valid_to,
                })
            self.env['hr.empgroup.details'].sudo().create(employee_data)
            return True

    def btn_select_all(self):
        self.ensure_one()  # Ensure the method is called on a single record
        dt_emp = self.env['hr.employeedepartment.details'].search([('cari_id', '=', self.id)])
        if dt_emp:
            dt_emp.sudo().write({'is_selected': True})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Search Employee'),
            'res_model': 'hr.employeedepartment',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'views': [(False, 'form')],
        }


class HrCariEmployeeDepartmentDetails(models.TransientModel):
    _name = 'hr.employeedepartment.details'
    _description = 'Search Employee Department Wizard'

    cari_id = fields.Many2one('hr.employeedepartment', string='Employee Cari ID', ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string='Department ID')
    employee_id = fields.Many2one('hr.employee', string='Employee Name', index=True)
    division_id = fields.Many2one('sanhrms.division', string='Divisi', related='employee_id.division_id', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department', string='Departemen',
                                         related='employee_id.hrms_department_id', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate', string='Direktorat', related='employee_id.directorate_id',
                                     store=True)
    nik = fields.Char('NIK')
    job_id = fields.Many2one('hr.job', string='Job Position', index=True)
    is_selected = fields.Boolean('Select', default=False)

    def btn_select_all(self):
        dt_emp = self.env['hr.employeedepartment.details'].sudo().search([('cari_id', '=', self.cari_id.id)])
        if dt_emp:
            dt_emp.write({
                'is_selected': True
            })