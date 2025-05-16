# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError



class HRTraining(models.Model):
    _inherit = 'hr.employee.certification'

    nik = fields.Char('NIK', related='employee_id.nik', store=True)


class HRTraining(models.Model):
    _name = 'hr.training'
    _description = 'Santosa HR Training'
    _inherit = [ 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Nama Pelatihan")
    branch_id = fields.Many2one('res.branch', default=lambda self: self.env.user.branch_id, required=True)
    certificate_name = fields.Char("Nama Sertipikat")
    active = fields.Boolean(default=True)
    is_bonding = fields.Boolean(default=False)
    readonly = fields.Boolean(default=False)
    date = fields.Datetime('Date Request', default=fields.Datetime.now, required=True)
    name_institusi = fields.Char('Institusi', required=True)
    name_trainer = fields.Char('Trainer', required=True)
    approved_by = fields.Many2one('res.users', 'Approval')
    location_training = fields.Char('Lokasi', required=True)
    level_skill = fields.Selection([
        ('basic', 'Dasar'),
        ('intermediate', 'Menengah'),
        ('advanced', 'Lanjutan')
    ], default='basic')
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
    ], required=True, default='internal')
    certification_types = fields.Selection([
        ('formal', 'Formal'),
        ('non_formal', 'Non Formal'),
        ('profesi', 'Profesi')
    ], string='Tipe Sertifikat', index=True, default='formal',
        help="Defines the certification type.")
    type_institution = fields.Many2one('res.type.institution',required=True, domain="[('code', '!=', 'el')]")
    certification_types_id = fields.Many2one('certification.type', string='Tipe Sertifikat', index=True,
        help="Defines the certification type.")
    certification_code = fields.Char(related='certification_types_id.code',store=True)
    date_start = fields.Date('Start Date Training',  default=fields.Date.today, required=True)
    date_end = fields.Date('Finish Training', required=True)
    
    @api.constrains('date_start','date_end','date_start_bond','date_end_bond')
    def _check_validation_training(self):
        for record in self:
            if record.date_start > record.date_end :
                raise UserError("harap masukan tangal peatihan yang sesuai")
            if record.date_start_bond > record.date_end_bond :
                raise UserError("harap masukan tanggal ikatan dinas yang benar")
            
    invoiceable = fields.Boolean(default=False)
    type_payment = fields.Selection([
        ('person', 'Per Person'),
        ('bulk', 'Bulking')
    ], string="Metode Pembayaran")
    amount = fields.Float('Nominal', default=0.0)
    skill_id = fields.Many2one('hr.skill',domain="('skill_type_id','=',skill_type_id.id)")
    skill_type_id = fields.Many2one('skill_type_id',domain="('name','!=','language')")
    total_amount = fields.Float('Total Nominal', compute="_compute_total_amount", store=True)
    employee_attende = fields.One2many('hr.training.attende', 'order_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('wip', 'Berlangsung'),
        ('fin', 'Selesai'),
        ('hold', 'Hold'),
        ('cancel', 'Batal'),
        ('done', 'Valid')
    ], default='draft', tracking=True)
    descr = fields.Text("Description")
    date_start_bond = fields.Date('Start Bonding', default=fields.Date.today)
    date_end_bond = fields.Date('End Bonding')
    
    @api.constrains('date_start','date_end','date_start_bond','date_end_bond')
    def _check_validation_training(self):
        for record in self:
            if record.date_start > record.date_end :
                raise UserError("harap masukan tangal peatihan yang sesuai")
            if record.date_start_bond > record.date_end_bond :
                raise UserError("harap masukan tanggal ikatan dinas yang benar")

    @api.depends('invoiceable', 'type_payment', 'amount', 'employee_attende.amount')
    def _compute_total_amount(self):
        for rec in self:
            if not rec.invoiceable:
                rec.total_amount = 0.0
            elif rec.type_payment == 'person':
                rec.total_amount = sum(att.amount for att in rec.employee_attende)
            elif rec.type_payment == 'bulk':
                rec.total_amount = rec.amount

    def act_done(self):
        for rec in self:
            for att in rec.employee_attende:
                if not att.results:
                    raise UserError('Harap inputkan Hasil Training')
                if att.results == 'pass':
                    if not att.date_start or not att.date_end:
                        raise UserError('Harap inputkan Masa berlaku Sertipikat')
                    if not att.no_certivicate:
                        raise UserError('Harap inputkan No Sertipikat')
                    progres = {'basic': 25, 'intermediate': 60, 'advanced': 95}[rec.level_skill]
                    skill_level = self.env['hr.skill.level'].search([
                        ('skill_type_id', '=', rec.skill_id.skill_type_id.id),
                        ('name', '=', f"{rec.skill_id.name}{progres}%"),
                        ('level_progress', '=', progres)
                    ], limit=1)

                    if not skill_level:
                        skill_level = self.env['hr.skill.level'].sudo().create({
                            'skill_type_id': rec.skill_id.skill_type_id.id,
                            'name': f"{rec.skill_id.name}{progres}%",
                            'level_progress': progres,
                            'default_level': True,
                        })
                    must = False
                    if rec.certification_code and rec.certification_code == 'pm':
                        must = True
                
                    certivicate = self.env['hr.employee.certification'].sudo().create({
                        'employee_id': att.employee_id.id,
                        'name': rec.certificate_name,
                        'number': att.no_certivicate,
                        'certification_types': rec.certification_types,
                        'type_institution': rec.type_institution.id,
                        'issuing_institution': rec.name_institusi,
                        'valid_from': att.date_start,
                        'valid_to': att.date_end,
                        'skill_id': rec.skill_id.id,
                        'must': must,
                        'certification_types_id' :rec.certification_types_id.id,
                        'is_dinas': att.is_bonding,
                        'date_from': rec.date_start_bond,
                        'date_to': rec.date_end_bond,
                        'active': True,
                        'is_expired': 'valid',
                        'remarks':  f"{att.employee_id.name} Telah LULUS dari Pelatihan {rec.name} dengan score {att.result_score} yang diadakan {rec.name_institusi} dari tanggal {rec.date_start} hingga {rec.date_end}."
                        })
                    att.certivicate_id = certivicate.id
                    self.env['hr.resume.line'].sudo().create({
                        'employee_id': att.employee_id.id,
                        'name': rec.name,
                        'date_start': rec.date_start,
                        'date_end': rec.date_end,
                        'description': f"{att.employee_id.name} Telah LULUS dari Pelatihan {rec.name} yang diadakan {rec.name_institusi} dari tanggal {rec.date_start} hingga {rec.date_end}."
                    })
                    # deliver to resume and skill employee
                    emp_skill = self.env['hr.employee.skill'].search([
                        ('employee_id', '=', att.employee_id.id),
                        ('skill_id', '=', rec.skill_id.id),
                        ('skill_type_id', '=', rec.skill_id.skill_type_id.id)
                    ], limit=1)
                    if not emp_skill:
                        self.env['hr.employee.skill'].sudo().create({
                            'employee_id': att.employee_id.id,
                            'skill_id': rec.skill_id.id,
                            'skill_type_id': rec.skill_id.skill_type_id.id,
                            'skill_level_id': skill_level.id
                        })
                    elif emp_skill.skill_level_id.level_progress < skill_level.level_progress:
                        emp_skill.sudo().write({
                            'skill_level_id': skill_level.id
                        })
            rec.readonly = True
            rec.state = 'done'

    def act_hold(self):
        self.write({'state': 'hold'})

    def act_wip(self):
        for training in self.env['hr.training'].search([]):
            if training.state == 'approve' and fields.Date.today() == training.date_start:
                training.write({'state': 'wip'})
            elif training.state == 'wip' and training.date_end and (training.date_end + timedelta(days=1)) == fields.Date.today():
                training.write({'state': 'fin'})

    def act_approve(self):
        self.write({
            'state': 'approve',
            'readonly': True,
            'approved_by': self.env.user.id
        })
        
    def act_cancel(self):
        self.write({
            'state': 'cancel',
            'readonly': True,
        })
    
    
    def unlink(self):
        return super(HRTraining, self).unlink()
    
class HRTrainingAttendee(models.Model):
    _name = 'hr.training.attende'
    _description = 'Santosa HR Training Attendee'

    order_id = fields.Many2one('hr.training')
    employee_id = fields.Many2one('hr.employee', string="Karyawan")
    nik = fields.Char('Employee NIK', related='employee_id.nik', store=True)
    name = fields.Char('Employee Name', related='employee_id.name', store=True)
    result_score = fields.Integer('Score', default=0)
    results = fields.Selection([
        ('failed', 'Tidak Lulus'),
        ('pass', 'Lulus')])
    periode = fields.Char(string='Periode', compute='_compute_periode', store=True)

    @api.depends('date_start')
    def _compute_periode(self):
        for record in self:
            record.periode = str(record.date_start.year) if record.date_start else ''
    
    certification_types_id = fields.Many2one('certification.type', string='Tipe Sertifikat', index=True,
        help="Defines the certification type.",related="order_id.certification_types_id")
     
    @api.constrains('date_start','date_end','date_start_bond','date_end_bond')
    def _check_validation_training(self):
        for record in self:
            if record.date_start > record.date_end :
                raise UserError("harap masukan tangal peatihan yang sesuai")
            if record.date_start_bond > record.date_end_bond :
                raise UserError("harap masukan tanggal ikatan dinas yang benar")
            
    certivicate_id = fields.Many2one('hr.employee.certification')
    no_certivicate = fields.Char('No Sertipikat')
    amount = fields.Float('Nominal', default=0.0,compute="_compute_type_payment")
    date_start = fields.Date('Valid From')
    date_end = fields.Date('Valid To')
    is_bonding = fields.Boolean(related="order_id.is_bonding")
    type_payment = fields.Selection(related='order_id.type_payment')
    certificate_name = fields.Char('Nama Sertifikat', compute='_compute_certificate_name', store=True)
    name_institusi = fields.Char('Institusi', compute='_compute_name_institusi', store=True)
    branch_id = fields.Many2one('res.branch')
    date_start_bond = fields.Date('Start Bonding',related="order_id.date_start_bond")
    date_end_bond = fields.Date('End Bonding',related="order_id.date_end_bond")
    state = fields.Selection(related='order_id.state')
    
    _sql_constraints = [
        (
            'constraint_unique_certification_training',
            'unique(order_id, employee_id)',
            'Tidak diperkenankan memasukan karyawan yang sama.'
        ),
        (
            'constraint_unique_certification',
            'unique(order_id, no_certivicate, name_institusi)',
            'Tidak diperkenankan memasukan memasukkan nomor sertipikat sama.'
        ),
    ]


    @api.depends('order_id.type_payment')
    def _compute_type_payment(self):
        for rec in self:
            rec.type_payment = rec.order_id.type_payment
            if rec.order_id.type_payment == 'person':
                rec.amount = rec.order_id.amount


    @api.depends('order_id.certificate_name')
    def _compute_certificate_name(self):
        for rec in self:
            rec.certificate_name = rec.order_id.certificate_name if rec.order_id else ''

    @api.depends('order_id.name_institusi')
    def _compute_name_institusi(self):
        for rec in self:
            rec.name_institusi = rec.order_id

    def unlink(self):
        return super(HRTrainingAttendee, self).unlink()

class HRSkill(models.Model):
    _inherit = 'hr.skill'    
    
    def unlink(self):
        return super(HRSkill, self).unlink()

class HRSkillType(models.Model):
    _inherit = 'hr.skill.type'  
    
    type = fields.Selection([('hard', 'Hard Skill'),('soft','Soft Skill'),('lang','Language')],'Type')  
    
    def unlink(self):
        return super(HRSkillType, self).unlink()

