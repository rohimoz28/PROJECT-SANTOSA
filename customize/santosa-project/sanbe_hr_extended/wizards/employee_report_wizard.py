from odoo import fields, models
from odoo.exceptions import UserError


class EmployeeExportWizard(models.TransientModel):
    _name = 'employee.report.wizard'
    _description = 'Employee Report Wizard'


    start_date = fields.Date(string='Periode')
    end_date = fields.Date(string='Sampai')
    branch_id = fields.Many2one(
        comodel_name = 'res.branch', 
        string = 'Unit Bisnis',
        domain = lambda self: [('id', 'in', self.env.user.branch_ids.ids)]
    )
    employee_group1s = fields.Many2one(comodel_name='emp.group', string='Group Penggajian')
    employee_levels = fields.Many2one(comodel_name='employee.level', string='Level karyawan')


    def button_export_pdf(self):
        self.ensure_one()

        emp_log_domain = []

        if self.start_date:
            emp_log_domain.append(('start_date', '>=', self.start_date))
        if self.end_date:
            emp_log_domain.append(('start_date', '<=', self.end_date))
        if self.branch_id:
            emp_log_domain.append(('bisnis_unit', '=', self.branch_id.id))
        if self.employee_group1s:
            emp_log_domain.append(('employee_id.employee_group1s', '=', self.employee_group1s.id))
        if self.employee_levels:
            emp_log_domain.append(('employee_id.employee_levels', '=', self.employee_levels.id))

        emp_log = self.env['hr.employment.log'].search(emp_log_domain)

        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_extended.employee_report_html',
            'report_type': 'qweb-html',
            'report_file': f'Employee_Report_{self.employee_group1s.name or "Semua"}',
            'context': {
                'active_model': 'hr.employment.log',
                'active_ids': emp_log.ids,  # semua record
            },
            'data': {
                'start_date_filter': str(self.start_date or '-'),
                'end_date_filter': str(self.end_date or '-'),
                'employee_group1s': self.employee_group1s.name or 'Semua',
                'employee_levels': self.employee_levels.name if self.employee_levels else 'Semua',
                'branch_id': (self.branch_id.name).upper() if self.branch_id else 'Semua',

            },
        }

    def button_export_excel(self):
        self.ensure_one()

        emp_log_domain = []

        if self.start_date:
            emp_log_domain.append(('start_date', '>=', self.start_date))
        if self.end_date:
            emp_log_domain.append(('start_date', '<=', self.end_date))
        if self.branch_id:
            emp_log_domain.append(('bisnis_unit', '=', self.branch_id.id))
        if self.employee_group1s:
            emp_log_domain.append(('employee_id.employee_group1s', '=', self.employee_group1s.id))
        if self.employee_levels:
            emp_log_domain.append(('employee_id.employee_levels', '=', self.employee_levels.id))

        emp_log = self.env['hr.employment.log'].search(emp_log_domain)

        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_extended.employee_report_excel',
            'report_type': 'xlsx',
            'report_file': f'Employee_Report_{self.employee_group1s.name or "Semua"}',
            'context': {
                'active_model': 'hr.employment.log',
                'active_ids': emp_log.ids,  # semua record
            },
            'data': {
                'start_date_filter': str(self.start_date or '-'),
                'end_date_filter': str(self.end_date or '-'),
                'employee_group1s': self.employee_group1s.name or 'Semua',
                'employee_levels': self.employee_levels.name if self.employee_levels else 'Semua',
                'branch_id': (self.branch_id.name).upper() if self.branch_id else 'Semua',

            },
        }
         