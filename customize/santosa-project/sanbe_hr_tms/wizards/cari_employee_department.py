
from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError


class HrCariEmployeeDepartment(models.TransientModel):
    _name = 'hr.employeedepartment'
    _description = 'Search Employee Department Wizard'

    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
    branch_id = fields.Many2one('res.branch', string='Bisnis Unit', index=True, domain="[('id','in',branch_ids)]")
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department', index=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', store=True)
    empgroup_id = fields.Many2one('hr.empgroup', string='Employee Group Setting', index=True)
    plan_id = fields.Many2one('hr.overtime.planning', string='Planning OT', index=True)
    plann_date_from = fields.Date('Plann Date From')
    plann_date_to = fields.Date('Plann Date To')
    ot_plann_from = fields.Float('OT Plann From')
    ot_plann_to = fields.Float('OT Plann To')
    approve_time_from = fields.Float('Approve Time From')
    approve_time_to = fields.Float('Approve Time To')
    machine = fields.Char('Machine')
    work_plann = fields.Char('Work Plann')
    output_plann = fields.Char('Output Plann')
    transport = fields.Boolean('Transport')
    meals = fields.Boolean('Meal')
    valid_from = fields.Date('Valid From', copy=True)
    valid_to = fields.Date('To', copy=True)
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
        'hr.department',
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
                allbranch = self.env['hr.department'].sudo().search([('branch_id', '=', allrecs.branch_id.id)])
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

    @api.onchange('area_id')
    def _isi_employee_area(self):
        for alldata in self:
            if not alldata.area_id:
                alldata.employee_ids = [Command.clear()]
                continue

            # Fetch employees in a single SQL query
            self.env.cr.execute("""
                SELECT id, department_id, nik, job_id
                FROM hr_employee
                WHERE state = 'approved' AND area = %s
            """, (alldata.area_id.id,))
            myemp = self.env.cr.fetchall()

            # Batch create employee details records
            datadetails = self.env['hr.employeedepartment.details']
            employee_data = []
            for allemp in myemp:
                employee_data.append({
                    'cari_id': alldata.id,
                    'department_id': allemp[1],
                    'employee_id': allemp[0],
                    'nik': allemp[2],
                    'job_id': allemp[3],
                    'is_selected': False,
                })
            if employee_data:
                datadetails |= datadetails.sudo().create(employee_data)
            alldata.employee_ids = datadetails.ids

    @api.onchange('area_id', 'branch_id')
    def _isi_employee_branch(self):
        for alldata in self:
            if not alldata.area_id or not alldata.branch_id:
                alldata.employee_ids = [Command.clear()]
                continue

            # Fetch employees for both area and branch
            self.env.cr.execute("""
                SELECT id, department_id, nik, job_id
                FROM hr_employee
                WHERE state = 'approved' AND area = %s AND branch_id = %s
            """, (alldata.area_id.id, alldata.branch_id.id))
            myemp = self.env.cr.fetchall()

            # Batch create employee details records
            datadetails = self.env['hr.employeedepartment.details']
            employee_data = []
            for allemp in myemp:
                employee_data.append({
                    'cari_id': alldata.id,
                    'department_id': allemp[1],
                    'employee_id': allemp[0],
                    'nik': allemp[2],
                    'job_id': allemp[3],
                    'is_selected': False,
                })
            if employee_data:
                datadetails |= datadetails.sudo().create(employee_data)
            alldata.employee_ids = datadetails.ids

    @api.onchange('department_id')
    def _isi_employee(self):
        for alldata in self:
            if not alldata.department_id:
                alldata.employee_ids = [Command.clear()]
                continue

            # Fetch employees by department in a single query
            self.env.cr.execute("""
                SELECT id, department_id, nik, job_id
                FROM hr_employee
                WHERE state = 'approved' AND department_id = %s
            """, (alldata.department_id.id,))
            myemp = self.env.cr.fetchall()

            # Batch create employee details records
            datadetails = self.env['hr.employeedepartment.details']
            employee_data = []
            for allemp in myemp:
                employee_data.append({
                    'cari_id': alldata.id,
                    'department_id': allemp[1],
                    'employee_id': allemp[0],
                    'nik': allemp[2],
                    'job_id': allemp[3],
                    'is_selected': False,
                })
            if employee_data:
                datadetails |= datadetails.sudo().create(employee_data)
            alldata.employee_ids = datadetails.ids

    def action_insert_empgroup(self):
        context_field = self._context.get('fieldname')
        employee_data = []

        if context_field == 'plan_id':
            # Processing for 'plan_id' context
            for emp in self.employee_ids.filtered(lambda e: e.is_selected):
                employee_data.append({
                    'planning_id': self.plan_id.id,
                    'area_id': emp.employee_id.area.id,
                    'branch_id': emp.employee_id.branch_id.id,
                    'department_id': emp.employee_id.department_id.id,
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
            if not self.wdcode:
                raise UserError('WD Code must be selected.')
            if not self.valid_from:
                raise UserError('Date Valid From must be selected.')
            if not self.valid_to:
                raise UserError('Date Valid To must be selected.')

            # Processing for other contexts
            for emp in self.employee_ids.filtered(lambda e: e.is_selected):
                employee_data.append({
                    'empgroup_id': self.empgroup_id.id,
                    'area_id': emp.employee_id.area.id,
                    'branch_id': emp.employee_id.branch_id.id,
                    'department_id': emp.department_id.id,
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
        dt_emp = self.env['hr.employeedepartment.details'].sudo().search([('cari_id', '=', self.id)])
        if dt_emp:
            dt_emp.write({
                'is_selected': True
            })
        
        return {
                'type': 'ir.actions.act_window',
                'name': _('Search Employee'),
                'res_model': 'hr.employeedepartment',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                'views': [[False, 'form']]
            }


class HrCariEmployeeDepartmentDetails(models.TransientModel):
    _name = 'hr.employeedepartment.details'
    _description = 'Search Employee Department Wizard'

    cari_id = fields.Many2one('hr.employeedepartment', string='Employee Cari ID', index=True)
    department_id = fields.Many2one('hr.department', string='Department ID', index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', index=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', store=True)
    nik = fields.Char('NIK')
    job_id = fields.Many2one('hr.job', string='Job Position', index=True)
    is_selected = fields.Boolean('Select', default=False)
    
    def btn_select_all(self):
        dt_emp = self.env['hr.employeedepartment.details'].sudo().search([('cari_id', '=', self.cari_id.id)])
        if dt_emp:
            dt_emp.write({
                'is_selected': True
            })
            