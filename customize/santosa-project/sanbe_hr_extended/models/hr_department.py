# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression

class HrDepartment(models.Model):
    _inherit = "hr.department"

    @api.model
    def default_get(self, default_fields):
        res = super(HrDepartment, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res
    
    # @api.model
    def unlink(self):
        return super(HrDepartment, self).unlink()

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            # mybranch = self.env['res.branch'].sudo().search([('branch_code','=','BU3')])
            mybranch = self.env.user.branch_id
            if  str(name).find('-') != -1:
                if len(name.split('-')) >2:
                    mycode = '%s-%s' % ( name.split('-')[0], name.split('-')[1])
                    nama = name.split('-')[2]
                    # user_ids = self.sudo()._search(expression.AND([[('department_code', '=', mycode),('branch_id','=',mybranch.id),'|',('name', 'ilike', nama),('branch_id','=',mybranch.id)], domain]), limit=1,
                    #                         order=order)
                    user_ids = self._search([('department_code', '=', mycode),('branch_id','=',mybranch.id),'|',('name', operator, nama),('branch_id','=',mybranch.id)], limit=limit,
                                            order=order)
                    return user_ids
                else:
                    search_domain = [('name', operator, name), ('branch_id', '=', mybranch.id), ]
                    user_ids = self._search(search_domain, limit=limit, order=order)
                    return user_ids
            else:
                search_domain = [('name',operator, name),('branch_id','=',mybranch.id),]
                # user_ids = self._search(search_domain, limit=limit, order=order)
                # return user_ids
                return super()._name_search(name, search_domain, operator, limit, order)
        else:
            return super()._name_search(name, domain, operator, limit, order)
    


class HRJob(models.Model):
    _inherit = "hr.job"

    @api.depends('area')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    area = fields.Many2one('res.territory',string='Area',tracking=True,)
    branch_ids = fields.Many2many('res.branch','res_branch_rel',string='AllBranch',compute='_isi_semua_branch',store=False)
    branch_id = fields.Many2one('res.branch',domain="[('id','in',branch_ids)]", string='Bisnis Unit')
    directorate_id = fields.Many2one('sanhrms.directorate', tracking=True, string='Direktorat')
    directorate_code = fields.Char('Directorate Code',related='directorate_id.directorate_code')

    department_id = fields.Many2one('hr.department', compute = '_find_department_id',  string='Departemen', store=True, required=False)
    hrms_department_id = fields.Many2one('sanhrms.department', tracking=True, string='Departemen')
    department_code = fields.Char('Departemen Code', related='hrms_department_id.department_code')
    division_id = fields.Many2one('sanhrms.division', tracking=True, string='Divisi')
    division_code = fields.Char('Divisi Code', related='division_id.division_code')
    display_name = fields.Char(compute='_compute_display_name', string='Display Name', store=True, readonly=True)

    _sql_constraints = [
        ('name_company_uniq', 'check(1=1)', 'The name of the job position must be unique per department in company!'),
        ('no_of_recruitment_positive', 'CHECK(no_of_recruitment >= 0)',
         'The expected number of new employees must be positive.')
    ]


    # @api.model
    def unlink(self):
        return super(HRJob, self).unlink()
    

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            # mybranch = self.env['res.branch'].sudo().search([('branch_code','=','BU3')])
            mybranch = self.env.user.branch_id
            search_domain = [('name', operator, name), ('branch_id', '=', mybranch.id)]
            # search_domain = [('name', operator, name),('branch_id','=',mybranch.id)]
            user_ids = self._search(search_domain + domain, limit=limit, order=order)
            return user_ids
        else:
            return super()._name_search(name, domain, operator, limit, order)

    @api.model
    def default_get(self, default_fields):
        res = super(HRJob, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id': self.env.user.branch_id.id or False
            })
        return res

    
    @api.depends('hrms_department_id')
    def _find_department_id(self):
        for line in self:
            if line.hrms_department_id:
                Department = self.env['hr.department'].search([('name', 'ilike', line.division_id.name)], limit=1)
                if Department:
                    line.department_id = Department.id
                else:
                    Department = self.env['hr.department'].sudo().create({
                        'name': line.hrms_department_id.name,
                        'active': True,
                        'company_id': self.env.user.company_id.id,
                    })
                    line.department_id = Department.id

    @api.model
    def create(self, vals):
        res = super(HRJob, self).create(vals)
        for allres in res:
            if not allres.branch_id:
                allres.branch_id = allres.department_id.branch_id.id
        return res

    
    @api.depends('name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name.upper()}"