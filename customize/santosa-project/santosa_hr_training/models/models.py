# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class HRTraining(models.Model):
    _name = 'hr.training'
    _description = 'Santosa HR Training'

    name = fields.Char("Nama Pelatihan")
    branch_id = fields.Many2one('res.branch')
    certificate_name = fields.Char("Nama Sertipikat")
    active = fields.Boolean()
    is_bonding = fields.Boolean('Ikatan Kontrak', default=False)
    date_start_bond = fields.Date('Ikatan Kontrak Mulai')
    date_end_bond = fields.Date('Ikatan Kontrak Akhit')
    readonly = fields.Boolean(default=False)
    date = fields.Datetime('Date Request',
        default=fields.Datetime.now, required=True)
    name_institusi = fields.Char('Institusi',required=True)
    name_trainer = fields.Char('Trainer',required=True)
    approved_by = fields.Many2one('res.users','Approval',)
    location_training = fields.Char('Lokasi',required=True)
    level_skill = fields.Selection([('basic','Dasar'),('intermediate','Menengah'),('advanced','Lanjutan')],default='basic')
    type = fields.Selection([('internal','Internal'),('external','External')],required=True, default='internal')
    date_start = fields.Date('Start Date Training',required=True)
    date_end = fields.Date('Finish Training',required=True)
    invoiceable = fields.Boolean(default=False)
    type_payment = fields.Selection([('none','None'),('person','Per Person'),('bulk','Bulking')],default='none')
    amount = fields.Float('Nominal', default=0.0)
    skill_id = fields.Many2one('hr.skill',required=True)
    total_amount = fields.Float('Total_Nominal', compute="_get_total_amt", default=0.0)
    employee_attende = fields.One2many('hr.training.attende','order_id')
    state = fields.Selection([('draft','Draft'),('approve','Approve'),('wip','In Process'),('done','Done')],'State')
    
    def unlink(self):
        return super(HRTraining, self).unlink()
    
    @api.depends('type_payment','amount','employee_attende')
    def _get_total_amtink(self):
        for line in self:
            if type_payment == 'none':
                line.total_amount = 0
                line.amount = 0
                for attende in line.aemployee_attende:
                    attende.amount = 0
            elif type_payment == 'person':                
                for attende in line.aemployee_attende:
                    line.total_amount += attende.amount
            elif type_payment == 'bulk':     
                line.total_amount = line.amount

    def act_done(self):
        for line in self:
            for attende in line.employee_attende:
                if not attende.results or line.certificate_name:
                    raise UserError('Harap inputkan Hasil Trainig')
                if not attende.date_start or attende.date_end:
                    raise UserError('Harap inputkan Masa berlaku Sertipikat')
                if not attende.no_certivicate:
                    raise UserError('Harap inputkan no Sertipikat')
                # attende.employee_id.
            line.state = 'done'
    
    def act_wip(self):
        for line in self:
            line.state = 'wip'

    def act_approve(self):
        for line in self:
            line.state = 'approve'
            line.readonly=True
            line.approved_by = self.env.user.id
    
class HRTrainingAttendee(models.Model):
    _name = 'hr.training.attende'
    _description = 'Santosa HR Training'

    order_id = fields.Many2one('hr.training')
    certificate_name = fields.Char("Nama Sertipikat", related="order_id.certificate_name")
    name_institusi = fields.Char('Institusi', related="order_id.name_institusi")
    branch_id = fields.Many2one('res.branch')
    nik = fields.Char('Employee NIK',related='employee_id.nik')
    name = fields.Char('Employee Name',related='employee_id.name')
    employee_id = fields.Many2one('hr.employee')
    result_score = fields.Integer('Score', default=0.0)
    type_payment = fields.Selection([('none','None'),('person','Per Person'),('bulk','Bulking')], related="order_id.type_payment")
    results = fields.Selection([('failed','Tidak Lulus'),('pass','Lulus')])
    certivicate_id = fields.Many2one('hr.certivicate')
    no_certivicate = fields.Char('No Certivicate')
    amount = fields.Float('Nominal', default=0.0)
    date_start = fields.Date('Valid From')
    date_end = fields.Date('Valid To')
    is_bonding = fields.Boolean(related="order_id.is_bonding",'Ikatan Dinas')
    start_bonding = fields.Date()
    finish_bonding = fields.Date()
    
    
    def unlink(self):
        return super(HRTrainingAttendee, self).unlink()
