# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo import api, fields, models, _, Command
EMP_GROUP1 = [
    ('Group1', 'Group 1 - Harian(pak Deni)'),
    ('Group2', 'Group 2 - bulanan pabrik(bu Felisca)'),
    ('Group3', 'Group 3 - Apoteker and Mgt(pak Ryadi)'),
    ('Group4', 'Group 4 - security(bu Susi)'),
    ('Group5', 'Group 5 - Tim promosi(pak Yosi)'),
    ('Group6', 'Group 6 - Adm pusat(pak Setiawan)'),
]

class HrSanbePayslip(models.Model):
    """Create new model for getting total Payroll Sheet for an Employee"""
    _name = 'hr.payroll.entry'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'id desc'
    _description = 'Sanbe HR Payroll'
    _rec_name = 'name'

    @api.model
    def _selection1(self):
        return EMP_GROUP1
    @api.depends('payroll_ids.amount_total','state')
    def hitung_total(self):
        for order in self:
            amount_total = 0.0
            for line in order.payroll_ids:
                amount_total += line.amount_total
            order.update({
                'net_sallary': amount_total,
            })

    name = fields.Char('Document Number',index=True)
    payroll_group = fields.Selection(selection=_selection1,
                                        default='Group2',
                                       string='Payroll Group')
    department_id  = fields.Many2one('hr.department',string='Department',index=True)
    employee_id = fields.Many2one('hr.employee',string='Employee',index=True)
    npwp = fields.Char('NPWP')
    job_id = fields.Many2one('hr.job',string='Job Position',index=True)
    job_status = fields.Selection([('permanent','Permanent'),
                                   ('contract','Contract')],
                                   default='contract', string='Job Status')
    emp_status = fields.Selection([('probation','Probation'),
                                   ('confirmed','Confirmed'),
                                   ('probation', 'Probation'),
                                   ('end_contract', 'End Of Contract'),
                                   ('resigned', 'Resigned'),
                                   ('retired', 'Retired'),
                                   ('terminated', 'Terminated'),
                                   ],string='Employment Status')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", tracking=True)
    net_sallary = fields.Float(digits=dp.get_precision('Payroll'), string="Total Net Sallary",
                          help="Total Net Sallary",compute='hitung_total',store=False)
    periode_pay_calc = fields.Many2one('hr.opening.closing',string='Periode Pay Calc')
    calc_date = fields.Date('Calc Date')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, 
                the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
    payroll_ids = fields.One2many('hr.payroll.details','payroll_id',auto_join=True,string='Payroll Details')




class HrSanbePayslipLine(models.Model):
    _name = 'hr.payroll.details'

    payroll_id = fields.Many2one('hr.payroll.entry',string='Payroll Entry ID', index=True)
    paycode = fields.Char('Pay Code')
    description = fields.Char('Description')
    payroll_type = fields.Char('Type')
    amount = fields.Float(digits=dp.get_precision('Payroll'), string="Amount",
                          help="Set Amount for line")
    quantity = fields.Float(digits=dp.get_precision('Payroll'), default=1.0,
                            string="Quantity", help="Set Qty for line")
    amount_total = fields.Float(digits=dp.get_precision('Payroll'), string="Amount Total",
                          help="Set Amount Total for line")




