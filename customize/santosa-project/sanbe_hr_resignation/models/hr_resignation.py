# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
from datetime import timedelta
from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
date_format = "%Y-%m-%d"


class HrResignation(models.Model):
    _inherit = 'hr.resignation'
    _order = 'create_date desc'


    def action_print_fkpd(self):
        """ Print report FKPD """
        return self.env.ref('sanbe_hr_resignation.fkpd_report').report_action(self)

    @api.onchange('name')
    @api.depends('name')
    def _isi_emps(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        # print(user.branch_id.name)
        for allrecs in self:
            allemps = self.env['hr.employee'].sudo().search(
                [('state', '=', 'approved'), ('active', '=', True), ('branch_id','=',user.branch_id.id)])
            allrecs.emp_nos_ids= [Command.set(allemps.ids)]

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    @api.depends('area','branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search([('branch_id','=', allrecs.branch_id.id)])
            allrecs.alldepartment =[Command.set(allbranch.ids)]

    name = fields.Char(
        string="Transaction Number",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    letter_no = fields.Char('Reference Number')
    area = fields.Many2one('res.territory',string='Area',tracking=True,)
    branch_ids = fields.Many2many('res.branch','res_branch_rel',string='AllBranch',compute='_isi_semua_branch',store=False)
    alldepartment = fields.Many2many('hr.department','hr_department_rel', string='All Department',compute='_isi_department_branch',store=False)
    branch_id = fields.Many2one('res.branch',string='Business Units',domain="[('id','in',branch_ids)]",tracking=True,)
    department_id = fields.Many2one('hr.department',domain="[('id','in',alldepartment)]",string='Sub Department')
    emp_no = fields.Char(string='Employee Nos', index=True, required=False, tracking=True)
    emp_nos_ids = fields.Many2many('hr.employee', 'res_emp_nos_resign_rel', string='AllEmpNos',
                                  compute='_isi_emps', store=False)
    emp_nos = fields.Many2one('hr.employee',string='Employee No',index=True,required=False,tracking=True, domain="[('id','in',emp_nos_ids)]")
    employee_name = fields.Char('Employee Name')
    emp_nik = fields.Char('NIK',index=True)
    # resignation_code = fields.Char('Resignation Code')
    trans_date= fields.Date('Transaction Date',default= fields.Date.today())
    trans_status = fields.Char('Trx Status')
    is_penalty = fields.Boolean('Penalty',default=False)
    penalty_amount = fields.Monetary('Pinalty Amount')
    submitted_date = fields.Date('Submited Date')
    resignation_date = fields.Date('Resignation Date')
    bondservice_from = fields.Date('Bond Services From')
    bondservice_to = fields.Date('To')
    effective_date = fields.Date('Effective Date')
    #penalty = fields.Char('Penalty')
    remarks = fields.Text('Remarks')
    images = fields.Many2many('ir.attachment', 'hr_resoignation_rel',string='Images',
                                          help="You may attach files to with this")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True,
        precompute=True,
        ondelete='restrict'
    )
    company_id = fields.Many2one('res.company',  default=lambda self: self.env.company,index=True)
    resignation_asset_ids = fields.One2many('hr.resignation.asset','resignation_id', autojoin=True, string='Asset Details')
    is_blacklist = fields.Boolean('Blacklist',default=False)
    contract_id = fields.Many2one('hr.contract',compute='hitung_masa_contract',string='Contract',index=True,store=False)
    contract_datefrom = fields.Date('Contract Date From',related='contract_id.date_start')
    contract_dateto = fields.Date('Contract Date To',related='contract_id.date_end')
    job_status = fields.Selection(related='emp_nos.job_status',default='contract',string='Job Status')
    keterangan = fields.Text('Keterangan')
    ws_month = fields.Integer('Working Service Month', related='emp_nos.ws_month',readonly=True)
    ws_year  = fields.Integer('Working Service Year', related='emp_nos.ws_year',readonly=True)
    ws_day = fields.Integer('Working Service Day', related='emp_nos.ws_day',readonly=True)

    cs_month = fields.Integer('Contract Service Month', compute='hitung_masa_contract',readonly=True,store=False)
    cs_year  = fields.Integer('Contract Service Year', compute='hitung_masa_contract',readonly=True,store=False)
    cs_day = fields.Integer('Contract Service Day', compute='hitung_masa_contract',readonly=True,store=False)
    # end_contract = fields.Boolean(string="Flag End of Contract", default=False)
    end_contract = fields.Boolean(string="Rehire", default=False)

    @api.depends('employee_contract','state','employee_id','job_status')
    def hitung_masa_contract(self):
        for record in self:
            service_util = False
            myear = 0
            mmonth = 0
            mday = 0
            mycont = self.env['hr.contract'].sudo().search([('employee_id','=',record.employee_id.id)],limit=1)
            if mycont:
                record.contract_id = mycont.id
                service_until = record.contract_dateto
                if record.contract_datefrom and service_until and service_until > record.contract_datefrom:
                    service_duration = relativedelta(
                        service_until, record.contract_datefrom
                    )
                    if service_duration.months == 11 and service_duration.days == 30:
                        record.cs_year = service_duration.years +1
                        record.cs_month = 0
                        record.cs_day = 0 #service_duration.days
                    else:
                        record.cs_year = service_duration.years
                        record.cs_month = service_duration.months
                        record.cs_day = service_duration.days

            else:
                record.cs_year = 0
                record.cs_month = 0
                record.cs_day = 0
                record.contract_id  = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        res = super(HrResignation,self)._onchange_employee_id()
        if self.employee_id:
            self.notice_period = self.employee_id.resign_notice
            self.bondservice_to = self.employee_id.service_to
            self.bondservice_from = self.employee_id.service_from
            self.joined_date = self.employee_id.join_date or self.emp_nos.joining_date

        return res

    @api.onchange('employee_contract','employee_id','state')
    def isi_kontrak(self):
        for rec in self:
            if not rec.employee_contract:
                return
            employee_contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id)])
            for contracts in employee_contract:
                #if contracts.state == 'open':
                rec.contract_id = contracts.id
            rec.joined_date = rec.employee_id.join_date

    @api.depends('company_id')
    def _compute_currency_id(self):
        for order in self:
            order.currency_id = order.company_id.currency_id

    def button_cari_data(self):
        return True
    
    @api.constrains('joined_date')
    def _check_joined_date(self):
        for resignation in self:
            return True

    @api.onchange('emp_nos')
    def isi_asset(self):
        for allrec in self:
            if not allrec.emp_nos:
                return
            allrec.resignation_asset_ids = [Command.set([])]
            allasset = self.env['hr.resignation.asset']
            allrec.emp_no = allrec.emp_nos.employee_id
            allrec.joined_date = allrec.emp_nos.join_date
            allrec.emp_nik = allrec.emp_nos.nik
            allrec.employee_id = allrec.emp_nos.id
            allrec.employee_name = allrec.emp_nos.name
            allrec.area = allrec.emp_nos.area.id
            allrec.branch_id = allrec.emp_nos.branch_id.id
            allrec.department_id = allrec.emp_nos.department_id.id
            allrec.bondservice_from = allrec.emp_nos.service_from
            allrec.bondservice_to = allrec.emp_nos.service_to
            allrec.trans_status = "draft"

            for allemp in allrec.emp_nos.asset_ids:
                allasset |= self.env['hr.resignation.asset'].sudo().create({
                                'asset_benefit_type':allemp.asset_name,
                                'aset_benefit_number': allemp.asset_number,
                                'product_uom_id': allemp.uom.id,
                                'product_qty': allemp.asset_qty,
                                'keterangan': allemp.keterangan})
            allrec.resignation_asset_ids = allasset.ids

    def action_confirm_resignation(self):
        res = super(HrResignation,self).action_confirm_resignation()
        for alldata in self:
            alldata.trans_status ='confirm'
        return res

    @api.model
    def create(self, vals):
        res = super(HrResignation, self).create(vals)
        for allres in res:
            employee = self.env['hr.employee'].sudo().browse(allres.emp_nos.id)
            employee.write({'state': 'hold'})
        return res

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
               group_name = self.env['res.groups'].search([('name','=','HRD CA')])
               cekgroup = self.env.user.id in group_name.users.ids
               if cekgroup:
                   for node in arch.xpath("//field"):
                          node.set('readonly', 'True')
                   for node in arch.xpath("//button"):
                          node.set('invisible', 'True')
        return arch, view
    
    # def action_approve_resignation(self):
    #     res = super(HrResignation,self).action_approve_resignation()
    #     self.env['hr.employment.log'].sudo().create({'employee_id': self.emp_nos.id,
    #                                                  'service_type': self.resignation_type[1].upper(),
    #                                                  'start_date': self.trans_date or fields.Datetime.today(),
    #                                                  'end_date': self.approved_revealing_date or fields.Datetime.today(),
    #                                                  'bisnis_unit': self.branch_id.id,
    #                                                  'department_id': self.emp_nos.department_id.id,
    #                                                  'job_title': self.emp_nos.job_id.name,
    #                                                  'job_status': self.emp_nos.jobs_tatus,
    #                                                  'emp_status': self.emp_nos.emp_status,
    #                                                  'model_name': 'hr.resignation',
    #                                                  'model_id': self.id,
    #                                                  'trx_number': self.name,
    #                                                  'doc_number': self.name,
    #                                                  'end_contract': self.end_contract,
    #                                                  })
    #     self.emp_nos.write({'state': 'hold'})
    #     return res
            
    
    def init(self):
        mycari = self.env['hr.resignation'].sudo().search([('effective_date','=',False)])
        for allcari in mycari:
            if allcari.emp_nos.job_status =='contract':
                allcari.effective_date= allcari.emp_nos.contract_id.date_end
                allcari.env.cr.commit()

class HrResignationAsset(models.Model):
    _name = 'hr.resignation.asset'
    _description = 'Hr Resignation Asset'

    resignation_id = fields.Many2one('hr.resignation',string='Resignation ID', index=True)
    asset_benefit_type = fields.Char('Asset Benefit Type')
    aset_benefit_number = fields.Char('Asset Benefit Number')
    product_uom_id = fields.Many2one('uom.uom',string='UOM')
    product_qty = fields.Integer('QTY')
    keterangan = fields.Text('Keterangan')
    is_return = fields.Boolean('Return',default=False)

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
               group_name = self.env['res.groups'].search([('name','=','HRD CA')])
               cekgroup = self.env.user.id in group_name.users.ids
               if cekgroup:
                   for node in arch.xpath("//field"):
                          node.set('readonly', 'True')
                   for node in arch.xpath("//button"):
                          node.set('invisible', 'True')
        return arch, view