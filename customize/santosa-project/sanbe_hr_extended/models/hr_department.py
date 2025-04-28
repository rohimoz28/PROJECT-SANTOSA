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
    department_id = fields.Many2one('hr.department', compute = '_find_department_id',  string='Departemen', store=True, required=False)
    hrms_department_id = fields.Many2one('sanhrms.department', tracking=True, string='Departemen')
    
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
                     
    division_id = fields.Many2one('sanhrms.division', tracking=True, string='Divisi')
    directorate_id = fields.Many2one('sanhrms.directorate', tracking=True, string='Direktorat')

    # @api.model
    # def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
    #     domain = domain or []
    #     if name:
    #         #mybranch = self.env['res.branch'].sudo().search([('branch_code','=','BU3')])
    #         mybranch = self.env.user.branch_id
    #         search_domain = [('name', operator, name),('branch_id','=',mybranch.id)]
    #         user_ids = self._search(search_domain, limit=1, order=order)
    #         return user_ids
    #     else:
    #         return super()._name_search(name, domain, operator, limit, order)

    @api.model
    def create(self, vals):
        res = super(HRJob, self).create(vals)
        for allres in res:
            if not allres.branch_id:
                allres.branch_id = allres.department_id.branch_id.id
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
