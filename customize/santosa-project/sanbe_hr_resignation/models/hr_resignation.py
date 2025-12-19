# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
from datetime import timedelta
from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
date_format = "%Y-%m-%d"


class HrResignation(models.Model):
    _inherit = 'hr.resignation'
    _order = 'create_date desc'

    def action_print_fkpd(self):
        """ Print report FKPD """
        return self.env.ref('sanbe_hr_resignation.fkpd_report').report_action(self)

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search(
                    [('name', '=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search(
                [('id', 'in', databranch)])
            allrecs.branch_ids = [Command.set(allbranch.ids)]

    @api.depends('area', 'branch_id')
    def _isi_department_branch(self):
        for allrecs in self:
            databranch = []
            allbranch = self.env['hr.department'].sudo().search(
                [('branch_id', '=', allrecs.branch_id.id)])
            allrecs.alldepartment = [Command.set(allbranch.ids)]

    name = fields.Char(
        string="Transaction Number",
        required=True, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))
    letter_no = fields.Char('Reference Number')
    area = fields.Many2one('res.territory', string='Area',
                           tracking=True, store=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel',
                                  string='AllBranch', compute='_isi_semua_branch', store=False)
    alldepartment = fields.Many2many('hr.department', 'hr_department_rel',
                                     string='All Department', compute='_isi_department_branch', store=False)
    branch_id = fields.Many2one(
        'res.branch', string='unit Bisnis',  related='employee_id.branch_id', store=True)
    directorate_id = fields.Many2one(
        'sanhrms.directorate', string='Direktorat', related='employee_id.directorate_id', store=True)
    hrms_department_id = fields.Many2one(
        'sanhrms.department', string='Departemen', related='employee_id.hrms_department_id', store=True)
    division_id = fields.Many2one(
        'sanhrms.division', string='Divisi', related='employee_id.division_id', store=True)
    job_id = fields.Many2one('hr.job', string='Jabatan',
                             related='employee_id.job_id', store=True)
    parent_id = fields.Many2one(
        'parent.hr.employee', string='Atasan Langsung', related="employee_id.parent_id", store=True)
    emp_id = fields.Char('ID Karyawan', related='employee_id.employee_id')
    emp_nik = fields.Char(related='employee_id.nik', string='NIK')
    trans_date = fields.Date('Transaction Date', default=fields.Date.today())
    trans_status = fields.Char('Trx Status')
    is_penalty = fields.Boolean('Penalty', default=False)
    penalty_amount = fields.Monetary('Pinalty Amount')
    submitted_date = fields.Date('Submited Date')
    resignation_date = fields.Date('Resignation Date')
    bondservice_from = fields.Date('Bond Services From')
    bondservice_to = fields.Date('To')
    first_date_join = fields.Date('First Date of Joining',
                                  related='employee_id.first_date_join', store=True,)
    joined_date = fields.Date(
        string="First Date of Joining",
        store=True,
        readonly=False
    )
    join_date = fields.Date(
        string="First Date of Joining",
        related='employee_id.join_date',
        store=True,
        readonly=False
    )
    effective_date = fields.Date('Effective Date')
    remarks = fields.Text('Remarks')
    images = fields.Many2many('ir.attachment', 'hr_resoignation_rel', string='Images',
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
    company_id = fields.Many2one(
        'res.company',  default=lambda self: self.env.company, index=True)
    resignation_asset_ids = fields.One2many(
        'hr.resignation.asset', 'resignation_id', autojoin=True, string='Asset Details')
    is_blacklist = fields.Boolean('Blacklist', default=False)
    contract_id = fields.Many2one(
        'hr.contract', compute='hitung_masa_contract', string='Contract', index=True, store=False)
    contract_datefrom = fields.Date(
        'Contract Date From', related='contract_id.date_start')
    contract_dateto = fields.Date(
        'Contract Date To', related='contract_id.date_end')
    job_status = fields.Selection(
        related='employee_id.job_status', default='contract', string='Job Status')
    keterangan = fields.Text('Keterangan')
    ws_month = fields.Integer(
        'Working Service Month', compute="_compute_working_duration", readonly=True)
    ws_year = fields.Integer('Working Service Year',
                             compute="_compute_working_duration", readonly=True)
    ws_day = fields.Integer('Working Service Day',
                            compute="_compute_working_duration", readonly=True)
    cs_month = fields.Integer(
        'Contract Service Month', compute='hitung_masa_contract', readonly=True, store=False)
    cs_year = fields.Integer(
        'Contract Service Year', compute='hitung_masa_contract', readonly=True, store=False)
    cs_day = fields.Integer(
        'Contract Service Day', compute='hitung_masa_contract', readonly=True, store=False)
    end_contract = fields.Boolean(string="Akhir Kontrak", default=False)
    effective_day = fields.Integer(
        'Rehire', default=35, store=True, help="Jenjang perekrutan ulang karyawan")

    @api.constrains("effective_day", "end_contract")
    def _check_effective_day(self):
        for record in self:
            if record.end_contract:
                if record.effective_day <= 0:
                    raise ValidationError(
                        "Tidak diperkenankan memasukan nilai dibawah 1 atau kosong")
            # else:
            #     record.effective_day = 0

    return_date = fields.Date(
        'Return Date', help="Tgl Rekrut karyawan Rehire", compute="_compute_return_date", store=True,)

    @api.depends('effective_date', 'effective_day', "end_contract")
    def _compute_return_date(self):
        for record in self:
            if record.end_contract and record.effective_date:
                if record.effective_date and record.effective_day:
                    # Odoo Fields.Date mendukung penjumlahan dengan timedelta
                    record.return_date = record.effective_date + \
                        timedelta(days=record.effective_day)
                else:
                    record.return_date = record.effective_date + \
                        timedelta(days=35)
            else:
                record.return_date = fields.Datetime.today() + \
                    timedelta(days=record.effective_day)

    # @api.depends('hrms_department_id')
    # def _find_department_id(self):
    #     for line in self:
    #         if line.hrms_department_id:
    #             Department = self.env['sanhrms.department'].search(
    #                 [('name', 'ilike', line.division_id.name)], limit=1)
    #             if Department:
    #                 line.department_id = Department.id
    #             else:
    #                 Department = self.env['sanhrms.department'].sudo().create({
    #                     'name': line.hrms_department_id.name,
    #                     'active': True,
    #                     'company_id': self.env.user.company_id.id,
    #                 })
    #                 line.department_id = Department.id

    # @api.depends('employee_id','state')
    # @api.onchange('employee_id')
    # def _compute_employee_exit(self):
    #     for record in self.filtered('employee_id'):
    #         record.job_id = record.employee_id.job_id
    #         record.hrms_department_id = record.employee_id.hrms_department_id
    #         record.company_id = record.employee_id.company_id
    #         record.area = record.employee_id.area.id
    #         record.branch_id = record.employee_id.branch_id.id
    #         record.emp_nik = record.employee_id.nik

    @api.onchange('employee_id')
    def _onchange_employee_data(self):
        """ Mengisi data secara otomatis saat employee_id dipilih di UI """
        for rec in self:
            if rec.employee_id:
                emp = rec.employee_id
                # Mengambil tanggal bergabung dari berbagai kemungkinan field di Employee
                # self.joined_date = join_dt
                self.emp_nik = emp.nik
                self.area = emp.area.id
                self.branch_id = emp.branch_id.id
                self.job_id = emp.job_id.id
                self.joined_date = self.join_date or self.first_date_join
                # Mencari kontrak aktif
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', emp.id),
                    ('state', '=', 'open')
                ], order='id desc', limit=1)
                if contract:
                    rec.contract_id = contract.id
                    rec.employee_contract = contract.name
                    rec.expected_revealing_date = contract.date_end

    @api.depends('employee_id')
    def _compute_employee_data(self):
        for record in self:
            if record.employee_id:
                emp = record.employee_id
                # record.joined_date = join_dt
                # record.first_date_join = join_dt
                record.emp_nik = emp.nik
                record.branch_id = emp.branch_id.id

                record.area = emp.area.id
                record.joined_date = emp.join_date or emp.first_date_join

    @api.depends('employee_contract', 'state', 'employee_id', 'job_status')
    def hitung_masa_contract(self):
        for record in self:
            service_util = False
            myear = 0
            mmonth = 0
            mday = 0
            mycont = self.env['hr.contract'].sudo().search(
                [('employee_id', '=', record.employee_id.id)], limit=1)
            if mycont:
                record.contract_id = mycont.id
                service_until = record.contract_dateto
                if record.contract_datefrom and service_until and service_until > record.contract_datefrom:
                    service_duration = relativedelta(
                        service_until, record.contract_datefrom
                    )
                    if service_duration.months == 11 and service_duration.days == 30:
                        record.cs_year = service_duration.years + 1
                        record.cs_month = 0
                        record.cs_day = 0  # service_duration.days
                    else:
                        record.cs_year = service_duration.years
                        record.cs_month = service_duration.months
                        record.cs_day = service_duration.days

            else:
                record.cs_year = 0
                record.cs_month = 0
                record.cs_day = 0
                record.contract_id = False

    @api.onchange('employee_contract', 'employee_id', 'state')
    def isi_kontrak(self):
        for rec in self:
            if not rec.employee_contract:
                return
            employee_contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id)], order='id desc', limit=1)
            for contracts in employee_contract:
                # if contracts.state == 'open':
                rec.contract_id = contracts.id
            rec.joined_date = rec.join_date or rec.first_date_join
            # rec.joined_date = rec.employee_id.join_date

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

    def action_confirm_resignation(self):
        res = super(HrResignation, self).action_confirm_resignation()
        for alldata in self:
            alldata.trans_status = 'confirm'
        return res
    
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view

    def write(self, vals_list):
        res = super(HrResignation, self).write(vals_list)
        for allrec in self:
            if allrec.state == 'open':
                empstatus = allrec.employee_id.emp_status
                allrec.employee_id.contract_id = allrec.id
                allrec.employee_id.contract_datefrom = allrec.date_start
                allrec.employee_id.contract_dateto = allrec.date_end
                mycari = self.env['hr.employment.log'].sudo().search([('employee_id', '=', allrec.employee_id.id), ('job_status', '=', 'contract'), (
                    'service_type', '=', allrec.contract_type_id.code), ('start_date', '=', allrec.date_start), ('end_date', '=', allrec.date_end)])
                if not mycari:
                    log = self.env['hr.employment.log'].sudo().create({'employee_id': allrec.employee_id.id,
                                                                       'service_type': allrec.contract_type_id.code,
                                                                       'start_date': allrec.date_start,
                                                                       'end_date': allrec.date_end,
                                                                       'bisnis_unit': allrec.branch_id.id,
                                                                       'department_id': allrec.hrms_department_id.id,
                                                                       'job_title': allrec.job_id.name,
                                                                       'job_status': 'contract',
                                                                       'emp_status': empstatus,
                                                                       'model_name': 'hr.contract',
                                                                       'model_id': allrec.id,
                                                                       'resignation_id': allrec.id,
                                                                       'employee_group1s': allrec.employee_id.employee_group1s,
                                                                       'doc_number': allrec.name,
                                                                       'end_contract': allrec.end_contract,
                                                                       'area': allrec.area.id,
                                                                       'directorate_id': allrec.directorate_id.id,
                                                                       'hrms_department_id': allrec.hrms_department_id.id,
                                                                       'division_id': allrec.division_id.id,
                                                                       'parent_id': allrec.employee_id.parent_id.id,
                                                                       })
                    if not log.area:
                        log.area = allrec.area.id
                        log.directorate_id = allrec.directorate_id.id
                        log.hrms_department_id = allrec.hrms_department_id.id
                        log.division_id = allrec.division_id.id
                        log.parent_id = allrec.employee_id.parent_id.id
                else:
                    mycari.sudo().write({
                        'end_contract': allrec.end_contract,
                        'area': allrec.area.id,
                        'bisnis_unit': allrec.branch_id.id,
                        'directorate_id': allrec.directorate_id.id,
                        'hrms_department_id': allrec.hrms_department_id.id,
                        'division_id': allrec.division_id.id,
                        'parent_id': allrec.employee_id.parent_id.id, })

    @api.depends("contract_datefrom", "contract_dateto")
    def _compute_working_duration(self):
        for record in self:
            if record.contract_datefrom and record.contract_dateto:
                service_until = record.contract_dateto
                if record.contract_datefrom and service_until > record.contract_datefrom:
                    service_duration = relativedelta(
                        service_until, record.contract_datefrom
                    )
                    record.ws_year = service_duration.years
                    record.ws_month = service_duration.months
                    record.ws_day = service_duration.days
                else:
                    record.ws_year = 0
                    record.ws_month = 0
                    record.ws_day = 0
            else:
                record.ws_year = 0
                record.ws_month = 0
                record.ws_day = 0


class HrResignationAsset(models.Model):
    _name = 'hr.resignation.asset'
    _description = 'Hr Resignation Asset'

    resignation_id = fields.Many2one(
        'hr.resignation', string='Resignation ID', index=True)
    asset_benefit_type = fields.Char('Asset Benefit Type')
    aset_benefit_number = fields.Char('Asset Benefit Number')
    product_uom_id = fields.Many2one('uom.uom', string='UOM')
    product_qty = fields.Integer('QTY')
    keterangan = fields.Text('Keterangan')
    is_return = fields.Boolean('Return', default=False)

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search(
                [('name', '=', 'HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view
