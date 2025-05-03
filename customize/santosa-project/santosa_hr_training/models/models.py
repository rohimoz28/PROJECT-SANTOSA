from odoo import models, fields, api
from odoo.exceptions import UserError


class HRTraining(models.Model):
    _name = 'hr.training'
    _description = 'Santosa HR Training'

    name = fields.Char("Nama Pelatihan")
    branch_id = fields.Many2one('res.branch')
    certificate_name = fields.Char("Nama Sertifikat")
    active = fields.Boolean(default=True)
    is_bonding = fields.Boolean()
    readonly = fields.Boolean(default=False)
    date = fields.Datetime('Date Request', default=fields.Datetime.now, required=True)
    name_institusi = fields.Char('Institusi', required=True)
    name_trainer = fields.Char('Trainer', required=True)
    approved_by = fields.Many2one('res.users', 'Approval')
    location_training = fields.Char('Lokasi', required=True)
    level_skill = fields.Selection([
        ('basic', 'Dasar'),
        ('intermediate', 'Menengah'),
        ('advanced', 'Lanjutan')], default='basic')
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')], required=True, default='internal')
    date_start = fields.Date('Start Date Training', required=True)
    date_end = fields.Date('Finish Training', required=True)
    invoiceable = fields.Boolean(default=False)
    type_payment = fields.Selection([
        ('person', 'Per Person'),
        ('bulk', 'Bulking')], string="Metode Pembayaran")
    amount = fields.Float('Nominal', default=0.0)
    skill_id = fields.Many2one('hr.skill', required=True)
    total_amount = fields.Float('Total Nominal', compute="_compute_total_amount", store=True)
    employee_attende = fields.One2many('hr.training.attende', 'order_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('wip', 'Berlangsung'),
        ('hold', 'Hold'),
        ('cancel', 'Cancel'),
        ('done', 'Selesai')], default='draft')
    descr = fields.Text("Description")
    date_start_bond = fields.Date('Start Bonding')
    date_end_bond = fields.Date('End Bonding')

    def unlink(self):
        return super(HRTraining, self).unlink()

    @api.depends('invoiceable', 'type_payment', 'amount', 'employee_attende.amount')
    def _compute_total_amount(self):
        for rec in self:
            if not rec.invoiceable:
                rec.total_amount = 0
                rec.amount = 0
            if rec.invoiceable and rec.type_payment == 'person':
                rec.total_amount = sum(att.amount for att in rec.employee_attende)
            elif rec.invoiceable and rec.type_payment == 'bulk':
                rec.total_amount = rec.amount

    def act_done(self):
        for rec in self:
            for att in rec.employee_attende:
                if not att.results:
                    raise UserError('Harap inputkan Hasil Training')
                if not att.date_start or not att.date_end:
                    raise UserError('Harap inputkan Masa berlaku Sertipikat')
                if not att.no_certivicate:
                    raise UserError('Harap inputkan No Sertipikat')
                if att.results == 'pass':
                    progres = 0
                    if rec.level_skill == 'basic':
                        progres = 25
                    elif rec.level_skill == 'intermediate':
                        progres = 60
                    else:
                        progres = 95

                    skill_level = self.env['hr.skill.level'].search(
                        [('skill_type_id', '=', rec.skill_id.skill_type_id.id),
                         ('name', '=', rec.skill_id.name + str(progres) + '%'), ('level_progress', '=', progres)],
                        limit=1)
                    if not skill_level:
                        skill_level = self.env['hr.skill.level'].sudo().create({
                            'skill_type_id': rec.skill_id.skill_type_id.id,
                            'name': rec.skill_id.name + str(progres) + '%',
                            'level_progress': progres,
                            'default_level': True,
                        })

                    certivicate = self.env['hr.employee.certification'].sudo().create({
                        'employee_id': att.employee_id.id,
                        'name': rec.certificate_name,
                        'number': att.no_certivicate,
                        'certification_types': 'formal',  # Or decide dynamically
                        'issuing_institution': rec.name_institusi,
                        'valid_from': att.date_start,
                        'valid_to': att.date_end,
                        'skill_id': rec.skill_id.id,
                        'is_dinas': att.is_bonding,
                        'date_from': rec.date_start_bond,
                        'date_to': rec.date_end_bond,
                        'active': True,
                        'is_expired': 'valid'
                    })
                    att.certivicate_id = certivicate.id
                    self.env['hr.resume.line'].sudo().create({
                        'employee_id': att.employee_id.id,
                        'name': rec.name,
                        'date_start': rec.date_start,
                        'date_end': rec.date_end,
                        'description': att.employee_id.name + ' ' + rec.name
                    })
                    level_emp_skill = self.env['hr.employee.skill'].search(
                        [('employee_id', '=', att.employee_id.id), ('skill_id', '=', rec.skill_id.id),
                         ('skill_type_id', '=', rec.skill_id.skill_type_id.id)])
                    if not level_emp_skill:
                        self.env['hr.employee.skill'].sudo().create({
                            'employee_id': att.employee_id.id,
                            'skill_id': rec.skill_id.id,
                            'skill_type_id': rec.skill_id.skill_type_id.id,
                            'skill_level_id': skill_level.id
                        })
                    elif level_emp_skill.skill_level_id.level_progress > skill_level.level_progress:
                        self.env['hr.employee.skill'].sudo().write({
                            'skill_level_id': skill_level.id
                        })
                    else:
                        pass
            rec.state = 'done'

    def act_cancel(self):
        self.write({'state': 'cancel'})

    def act_hold(self):
        self.write({'state': 'hold'})

    def act_wip(self):
        self.write({'state': 'wip'})

    def act_approve(self):
        self.write({
            'state': 'approve',
            'readonly': True,
            'approved_by': self.env.user.id
        })


class HRTrainingAttendee(models.Model):
    _name = 'hr.training.attende'
    _description = 'Santosa HR Training Attendee'

    order_id = fields.Many2one('hr.training')
    employee_id = fields.Many2one('hr.employee')
    nik = fields.Char('Employee NIK', related='employee_id.nik')
    name = fields.Char('Employee Name', related='employee_id.name')
    result_score = fields.Integer('Score', default=0)
    results = fields.Selection([
        ('failed', 'Tidak Lulus'),
        ('pass', 'Lulus')])
    certivicate_id = fields.Many2one('hr.certivicate')
    no_certivicate = fields.Char('No Sertipikat')
    amount = fields.Float('Nominal', default=0.0)
    date_start = fields.Date('Valid From')
    date_end = fields.Date('Valid To')
    is_bonding = fields.Boolean()

    # Computed version of related field to avoid parse error
    type_payment = fields.Selection([
        ('none', 'None'),
        ('person', 'Per Person'),
        ('bulk', 'Bulking')],
        string='Type Payment',
        compute='_compute_type_payment',
        store=True,
        readonly=True
    )

    certificate_name = fields.Char('Nama Sertifikat', compute='_compute_certificate_name', store=True)
    name_institusi = fields.Char('Institusi', compute='_compute_name_institusi', store=True)
    branch_id = fields.Many2one('res.branch')

    def unlink(self):
        return super(HRTrainingAttendee, self).unlink()

    @api.depends('order_id.type_payment')
    def _compute_type_payment(self):
        for rec in self:
            rec.type_payment = rec.order_id.type_payment

    @api.depends('order_id.certificate_name')
    def _compute_certificate_name(self):
        for rec in self:
            rec.certificate_name = rec.order_id.certificate_name

    @api.depends('order_id.name_institusi')
    def _compute_name_institusi(self):
        for rec in self:
            rec.name_institusi = rec.order_id.name_institusi