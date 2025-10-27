from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    """Extended model for HR employees with additional features."""
    _inherit = 'hr.employee'


    ptkp = fields.Selection(selection=[('TK0', "TK0"),
                                        ('TK1', "TK1"),
                                        ('TK2', "TK2"),
                                        ('TK3', "TK3"),
                                        ('K0', "K0"),
                                        ('K1', "K1"),
                                        ('K2', "K2"),
                                        ('K3', "K3"),],
                                    string="PTKP", default='TK0')
    exp_sim_no = fields.Date('License Expiration Date')
    emp_status_id = fields.Many2one('hr.emp.status', string='Employment Status', tracking=True)
    status = fields.Char(related='emp_status_id.status')

    _sql_constraints = [
        # ('nik_uniq', 'check(1=1)', "The NIK  must be unique, this one is already assigned to another employee."),
        # ('no_ktp_uniq', 'check(1=1)', "The NO KTP  must be unique, this one is already assigned to another employee."),
        # ('no_npwp_uniq', 'check(1=1)',
        #  "The NO NPWP  must be unique, this one is already assigned to another employee."),
        # ('identification_id_uniq', 'check(1=1)',
        #  "The Identification ID  must be unique, this one is already assigned to another employee."),
        ('contract_id_unique', 'UNIQUE(contract_id)', "Contract must be unique, this one is already assigned to another employee."),
    ]

    @api.model
    def write(self, vals):
        # for vals in vals_list:
        # _logger.info("Starting write method for hr.employee with vals: %s", vals)

        if vals.get('job_status'):
            if vals.get('job_status') == 'contract':
                vals['retire_age'] = 0
                vals['periode_probation'] = 0
                vals['joining_date'] = False

        if vals.get('nik'):
            gnik = vals.get('nik')
        else:
            gnik = self.nik

        if vals.get('badges_nos'):
            noss = vals.get('badges_nos')
            try:
                nos = noss[0][2][0]
            except:
                pass
                nos = noss[0][1]
            dat = self.env['hr.machine.details'].sudo().search([('id', '=', nos)], limit=1)
            if dat:
                dat.write({
                    'employee_id': self.id
                })
        
        if 'emp_status' in vals:
            emp_status_record = self.env['hr.emp.status'].search([('emp_status', '=', vals['emp_status'])], limit=1)
            vals['emp_status_id'] = emp_status_record.id if emp_status_record else False
        
        if 'emp_status_id' in vals:
            emp_status_record = self.env['hr.emp.status'].search([('id', '=', vals['emp_status_id'])], limit=1)
            vals['emp_status'] = emp_status_record.emp_status if emp_status_record else False

        # for record in self:
        #     job_status = vals.get('job_status', record.job_status)
        #     emp_status = vals.get('emp_status', record.emp_status)
        #     _logger.info("Validating emp_status: %s for job_status: %s", emp_status, job_status)
        #     if emp_status:
        #         record._validate_emp_status(job_status, emp_status)
        
        res = super(HrEmployee, self).write(vals)

        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        contractid = False
        existing = False
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('employee_id', _("New")) == _("New"):
                vals['employee_id'] = self.env['ir.sequence'].next_by_code(
                    'hr.employee.sequence') or _("New")
            # if vals.get('nik', _("New")) == _("New"):
            #     mycomp = self.env['res.company'].browse(vals.get('company_id'))
            #     dcomp = False
            #     bcode = False
            #     if mycomp.name=="PT.Sanbe Farma":
            #         dcomp='1'
            #         mybranch = self.env['res.branch'].sudo().browse(vals.get('branch_id'))
            #         if mybranch.branch_code == 'BU1':
            #             bcode= '01'
            #         elif mybranch.branch_code == 'BU2':
            #             bcode= '02'
            #         elif mybranch.branch_code=='RND':
            #             bcode= '03'
            #         elif mybranch.branch_code=='CWH':
            #             bcode= '04'
            #         elif mybranch.branch_code== 'BU3':
            #             bcode= '05'
            #         elif mybranch.branch_code =='BU4':
            #             bcode= '06'
            #         elif mybranch.branch_code == 'BU5':
            #             bcode= '07'
            #         elif mybranch.branch_code =='BU6':
            #             bcode= '08'
            #         elif mybranch.branch_code =='SBE':
            #             bcode='09'
            #         elif mybranch.branch_code == 'CWC':
            #             bcode = 10

            if vals.get('job_status'):
                if vals.get('job_status') == 'contract':
                    vals['retire_age'] = 0
                    vals['periode_probation'] = 0
                    vals['joining_date'] = False

            if vals.get('contract_id'):
                contractid = vals.get('contract_id')
                existing = self.env['hr.employee'].sudo().search([('name', '=', vals.get('name'))])
            # else:
            #     print('ini kemari ', vals.get('name'))
            #     return super(HrEmployee,self).create(vals_list)
            if 'emp_status_id' in vals:
                emp_status_record = self.env['hr.emp.status'].search([('id', '=', vals['emp_status_id'])], limit=1)
                vals['emp_status'] = emp_status_record.emp_status if emp_status_record else False
                
        res = super(HrEmployee, self).create(vals_list)
        if existing:
            #     print('ini bener ',existing.name)
            mycontract = self.env['hr.contract'].browse(contractid)
            myemps = self.env['hr.employee'].sudo().browse(mycontract.employee_id.id)
            myemps.unlink()
            mycontract.write({'employee_id': res.id})
        
        return res

    
    @api.depends('job_status')
    def _get_domain_emp_status_id(self):
        print("kedua")
        for record in self:
            if record.job_status == 'contract':
                return [('id', '=', 1)]
            elif record.job_status == 'permanent':
                return [('id', 'in', [1, 2])]
            else:
                return []
