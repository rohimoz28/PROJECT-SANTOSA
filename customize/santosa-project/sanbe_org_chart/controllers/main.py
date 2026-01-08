# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main

import logging
_logger = logging.getLogger(__name__)

class OrgChart(http.Controller):

	@http.route('/orgchart/update', methods=['POST'], csrf=False)
	def update_org_chart(self, child, last_parent, new_parent):
		# print('update data')
		if new_parent:
			# print('child ', child)
			# print('new parent ',new_parent)
			emp = request.env['hr.department'].search([('id','=',child)])
			bawal = request.env['res.branch'].sudo().search([('id','=',child)])
			# print('apa branch bukan %s branch names %s '%(bawal.id, bawal.name))
			mybranch = request.env['res.branch'].sudo().search([('id','=',new_parent)])
			# print('branch %s branch id %s'%(mybranch.name, mybranch.id))
			parent = request.env['hr.department'].search([('id','=',new_parent)])
			cekbranch = request.env['res.branch'].sudo().browse(int(parent.branch_id.id))
			# print('cek branch  %s  id branch  %s '%(cekbranch.name,cekbranch.id))
			emp.write({'parent_id': parent.id,'branch_id': mybranch.id})
			# print('write data ',emp)
			# print('new parent department  %s  id new  %s  new branch id  %s new branch name  %s parent id  %s '%(parent.id, parent.name,parent.branch_id.id, parent.branch_id.name,parent.parent_id.id))
			# print('emp branch name %s emp branch id %a employee name %s'%(emp.branch_id.name, emp.branch_id.id, emp.name))
		return ""

	@http.route('/orgchart/ondrop', type='json', auth="user")
	def ondrop_org_chart(self, employee_id):
		if employee_id:
			emp = request.env['hr.department'].search([('id','=',employee_id)])
			if emp:
				childs = request.env['hr.department'].search([('parent_id','=',emp.id)])
				if childs:
					childs_number = request.env['hr.department'].search_count([('parent_id','=',emp.id)])
					return {
						'name': 'Keep or Change Hierarchy',
						'type': 'ir.actions.act_window',
						'res_model': 'slife.employee',
						'view_mode': 'form',
						'view_type': 'form',
						'views': [[False, 'form']],
						'target': 'new',
						'context': {'parent_id': emp.id, 'childs_number': childs_number},
					}

		return {'result': False}
