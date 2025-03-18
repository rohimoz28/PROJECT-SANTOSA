from odoo import api, fields, models, _
class HrEmpStatus(models.Model):
    _name = 'hr.emp.status'
    _description = "Employee Status"
    _rec_name = 'name'

    status = fields.Char(string='Job Status')
    name = fields.Char(string='Nama')
    emp_status = fields.Char(string='Emp Status')

    # @api.compute('job_status')
    # def _compute_job_status(self):
    #     for rec in self:
    #         emp_status_domain=self.env['hr.emp.status'].sudo().search([])
    #         print(emp_status_domain.job_status)

    