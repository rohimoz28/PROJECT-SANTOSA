# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api, _

class HREmployee(models.Model):
    _inherit = "hr.employee"


    servicelog_ids = fields.One2many('hr.employment.log','employee_id',auto_join=True,string='Employement List')