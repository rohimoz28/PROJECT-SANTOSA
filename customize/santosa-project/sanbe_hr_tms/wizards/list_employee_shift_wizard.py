
import logging
import os
import csv
import tempfile
import base64
from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError,UserError
import logging

_logger = logging.getLogger(__name__)

from xlrd import open_workbook


class HrCariEmployeeShift(models.TransientModel):
    _name = 'wiz.employee.shift'
    _description = 'Search Employee Shift Wizard'

    target_models = fields.Char()
    periode_id = fields.Many2one(
        'hr.opening.closing',
        string='Period',
        index=True,
        default=lambda self:self._get_running_periode(),
        domain="[('state_process','in',('draft','running')),('branch_id','=',branch_id)]" 
    )
    period_text = fields.Char(string='Period Text', compute='_compute_period_text', store=True, index=True)
    target_process = fields.Selection([('generate','Generate Data'),
                                       ('shif to EMP','Process shift to EMP'),
                                       ('process xls','Process XLS')],'Process',default='generate')
    area_id = fields.Many2one('res.territory', string='Area ID', index=True, default=lambda self: self.env.user.branch_id.territory_id.id)
    branch_id = fields.Many2one('res.branch', string='Bisnis Unit', index=True, domain="[('id','in',branch_ids)]", default=lambda self: self.env.user.branch_id.id)
    department_id = fields.Many2one('hr.department', domain="[('id','in',alldepartment)]", string='Sub Department', index=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',string='Departemen', store=True)
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', store=True)
    files_name = fields.Char(string='File Upload', store=True)
    files_data = fields.Binary('File Upload')
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
        store=False
    )
    employee_ids = fields.One2many(
        'wiz.employee.shift.detail',
        'cari_id',
        auto_join=True,
        string='Cari Employee Details'
    )
    # empgroup_id = fields.Many2one('hr.empgroup', string='Cari Employee Group')

    # @api.onchange('periode_id')
    # def _onchange_periode_id(self):
    #     if self.periode_id:
    #         branch_id = self.periode_id.branch_id.id
    #         shifts = self.env['sb.employee.shift'].search([('periode_id', '=', self.periode_id.id)])
    #         directorate_ids = shifts.mapped('directorate_id.id')
    #         department_ids = shifts.mapped('hrms_department_id.id')
    #         division_ids = shifts.mapped('division_id.id')

    #         domain = [
    #             ('branch_id', '=', branch_id),
    #             ('directorate_id', 'in', directorate_ids),
    #             ('hrms_department_id', 'in', department_ids),
    #             ('division_id', 'in', division_ids),
    #             ('state', '=', 'draft'),
    #         ]
    #         return {'domain': {'empgroup_id': domain}}
    #     else:
    #         return {'domain': {'empgroup_id': []}}

    empgroup_id = fields.Many2one(
        'hr.empgroup',
        string='Cari Employee Group',
        domain=lambda self:self.find_periode_id()
    )

    @api.depends('periode_id')
    def find_periode_id(self):
        if self.periode_id:
            branch_id = self.periode_id.branch_id.id
            shifts = self.env['sb.employee.shift'].search([('periode_id', '=', self.periode_id.id)])
            directorate_ids = shifts.mapped('directorate_id.id')
            department_ids = shifts.mapped('hrms_department_id.id')
            division_ids = shifts.mapped('division_id.id')

            domain = [
                ('branch_id', '=', branch_id),
                ('directorate_id', 'in', directorate_ids),
                ('hrms_department_id', 'in', department_ids),
                ('division_id', 'in', division_ids),
                ('state', '=', 'draft'),
            ]
            empgroups = self.env('hr.empgroup').search(domain)
            return  [('id', 'in', [empgroups.ids])]


    # @api.onchange('periode_id')
    # def _onchange_periode_id(self):
    #     if self.periode_id:
    #         branch_id = self.periode_id.branch_id.id
    #         shifts = self.env['sb.employee.shift'].search([('periode_id', '=', self.periode_id.id)])
    #         directorate_ids = shifts.mapped('directorate_id.id')
    #         department_ids = shifts.mapped('hrms_department_id.id')
    #         division_ids = shifts.mapped('division_id.id')

    #         domain = [
    #             ('branch_id', '=', branch_id),
    #             ('directorate_id', 'in', directorate_ids),
    #             ('hrms_department_id', 'in', department_ids),
    #             ('division_id', 'in', division_ids),
    #             ('state', '=', 'draft'),
    #         ]
    #     else:
    #         domain = [('state', '=', 'draft'),]
    #     return {'domain': {'empgroup_id': domain}}

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
    
    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]
    
    

    def _get_filtered_employees_domain(self):
        """
        Build domain to filter employees based on selected fields.
        """
        domain = [('state', '=', 'approved'),('emp_status_id', '!=', False)]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        if self.hrms_department_id:
            domain.append(('hrms_department_id', '=', self.hrms_department_id.id))
        if self.directorate_id:
            domain.append(('directorate_id', '=', self.directorate_id.id))
        if self.division_id:
            domain.append(('division_id', '=', self.division_id.id))
        return domain
    
    def btn_search(self):
        for line in self: 
            line.employee_ids = False     
            
            if line.target_process == 'generate':          
                domain = line._get_filtered_employees_domain()
                employees = self.env['hr.employee'].search(domain)
                print(domain)
                if len(employees) <1:
                    raise UserError('Employee Not Found')
                for emp in employees:
                    self.env['wiz.employee.shift.detail'].create({
                        'cari_id': self.id,
                        'employee_id': emp.id,
                        'nik': emp.nik,
                        'directorate_id':emp.directorate_id.id,
                        'hrms_department_id':emp.hrms_department_id.id,
                        'division_id':emp.division_id.id,   
                        'department_id':emp.department_id.id,
                        'job_id':emp.job_id.id,
                        'is_selected': False
                    })
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Search Employee'),
                    'res_model': 'wiz.employee.shift',
                    'view_mode': 'form',
                    'target': 'new',
                    'res_id': self.id,
                    'views': [(False, 'form')],
                }
            elif line.target_process == 'shif to EMP':
                pass
            else:
                pass
        
    def btn_select_all(self):
        for line in self:
            for list_employee in line.employee_ids:
                if not list_employee.is_selected:
                    list_employee.is_selected = True
            return {
                'type': 'ir.actions.act_window',
                'name': _('Search Employee'),
                'res_model': 'wiz.employee.shift',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                'views': [(False, 'form')],
            }
        
    def action_process(self):
        self.ensure_one()
        for line in self:
            if line.target_process == 'generate':
                selected_lines = line.employee_ids.filtered(lambda line: line.is_selected)
                if not selected_lines:
                    raise UserError(_("Please select at least one line to apply settlement."))
                for line_employee in selected_lines:
                    self.env['sb.employee.shift'].create({
                         'periode_id':line.periode_id.id,
                         'period_text':line.period_text,
                         'employee_id':line_employee.employee_id.id,
                    })
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Employee Shift'),
                    'res_model': 'sb.employee.shift',
                    'view_mode': 'tree',
                    'target': 'current',
                    'views': [(False, 'tree')],
                }
            elif line.target_process == 'shif to EMP':
                if line.periode_id.id and line.empgroup_id.id:
                    try:
                        self.env.cr.execute("select generate_shift_empgroup(%s, %s)", (line.periode_id.id, line.empgroup_id.id))
                        self.env.cr.commit()
                        _logger.info("Stored procedure executed successfully for period: %s to Group Employee %s", line.periode_id.name,line.empgroup_id.name)
                    except Exception as e:
                        _logger.error("Error calling stored procedure: %s", str(e))
                        raise UserError("Error executing the function: %s" % str(e))
            else:
                pass
                
            
    @api.depends('periode_id.open_periode_from', 'periode_id.open_periode_to', 'periode_id.name', 'periode_id.branch_id')
    def _compute_period_text(self):
        """Menghitung teks periode."""
        for rec in self:
            if rec.periode_id:
                periode = rec.periode_id
                date_from = fields.Date.to_string(periode.open_periode_from) if periode.open_periode_from else ''
                date_to = fields.Date.to_string(periode.open_periode_to) if periode.open_periode_to else ''
                
                formatted_from = fields.Datetime.from_string(date_from).strftime('%d/%m') if date_from else ''
                formatted_to = fields.Datetime.from_string(date_to).strftime('%d/%m') if date_to else ''
                
                period_name = periode.name or ''
                
                rec.period_text = f"{formatted_from} - {formatted_to} {period_name}"
            else:
                rec.period_text = False
                
                
                
                # ===========================
                


    @api.model
    def csv_validator(self, xml_name):
        name, extension = os.path.splitext(xml_name)
        # Ubah .lower() agar lebih aman
        return True if extension.lower() in ('.xls', '.xlsx') else False
                
    
class HrCariEmployeeShiftDetails(models.TransientModel):
    _name = 'wiz.employee.shift.detail'
    _description = 'Search Employee Shift Wizard'

    cari_id = fields.Many2one('wiz.employee.shift', string='Employee Cari ID', ondelete='cascade', index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', index=True)
    directorate_id = fields.Many2one(related='employee_id.directorate_id', string='Direktorat', store=True, index=True, readonly=True)
    hrms_department_id = fields.Many2one(related='employee_id.hrms_department_id', string='Departemen', store=True, index=True, readonly=True)
    division_id = fields.Many2one(related='employee_id.division_id', string='Divisi', store=True, index=True, readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Sub Department', store=True, index=True, readonly=True) 
    nik = fields.Char('NIK')
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', index=True)
    is_selected = fields.Boolean('Select', default=False)
    
    def btn_select_all(self):
        dt_emp = self.env['hr.employeedepartment.details'].sudo().search([('cari_id', '=', self.cari_id.id)])
        if dt_emp:
            dt_emp.write({
                'is_selected': True
            })
            