# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    """Extended model for HR employees with additional features."""
    _inherit = 'hr.employee'

    branch_id = fields.Many2one('res.branch',string='Bussines Unit')
