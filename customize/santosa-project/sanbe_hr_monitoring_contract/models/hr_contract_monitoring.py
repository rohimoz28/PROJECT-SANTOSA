from odoo import fields, models, tools, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from itertools import groupby
import logging

_logger = logging.getLogger(__name__)


table_header = """
<br/>
<p>Dengan hormat, kami ingin mengingatkan bahwa terdapat beberapa karyawan yang kontraknya akan segera berakhir. Berikut adalah daftar karyawan yang kontraknya mendekati tanggal berakhirnya:</p>
<br/>
<table border="1" cellpadding="5" cellspacing="0">
    <thead>
        <tr>
            <th>Area</th>
            <th>Business Units</th>
            <th>Sub Department</th>
            <th>Nama Karyawan</th>
            <th>Job Position</th>
            <th>Immediate Superior</th>
            <th>End Date</th>
        </tr>
    </thead>
    <tbody>
"""        


table_footer = """
        </tbody>
    </table>
    <br/> 
    <p>Mohon untuk melakukan verifikasi dan tindakan lebih lanjut sesuai dengan kebijakan perusahaan.</p>
    <br/>
    <p>Terima kasih atas perhatian dan kerjasamanya.</p>
    <br/>
    <p>Salam hormat,</p>
    <br/>
    <br/>
                
    """

# def roman_list():
#     return[
#         (12,'XII'),(0,'-'),(1,'I'),(2,'II'),(3,'III'),
#         (4,'IV'),(5,'V'),(6,'VI'),(7,'VII'),
#         (8,'VIII'),(9,'IX'),(10,'X'),(11,'Xi')
#     ]

def month_to_roman(month):
    roman_list = [
        (0, '-'), (1, 'I'), (2, 'II'), (3, 'III'), 
        (4, 'IV'), (5, 'V'), (6, 'VI'), (7, 'VII'), (8, 'VIII'), 
        (9, 'IX'), (10, 'X'), (11, 'XI'),(12, 'XII')
    ]
    if 0 <= month <= 12:
        return roman_list[month][1]
    else:
        return "Invalid month"

bulan_map = {
    '01': 'Januari', '02': 'Februari', '03': 'Maret',
    '04': 'April', '05': 'Mei', '06': 'Juni',
    '07': 'Juli', '08': 'Agustus', '09': 'September',
    '10': 'Oktober', '11': 'November', '12': 'Desember'
}

# digunakan sebagai view sql untuk 
# monitoring contract yang running
class HrEmployeeContractMonitoring(models.Model):
    _auto = False
    _name = 'hr.employee.contract.monitoring'
    _description = 'Employee Contract Monitoring'
    _order = 'time_limit, start_notice'

    id = fields.Integer('ID', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_name = fields.Char('Employee Name', required=True)
    emp_id = fields.Char('ID Karyawan', required=True)
    nik_employee = fields.Char('Employee NIK', required=True)
    nik_lama = fields.Char('Old NIK', required=True)
    employee_address = fields.Char('Address', required=True)
    status_employee = fields.Char(string='Employee Status', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    company_name = fields.Char('Company Name', required=True)
    branch_id = fields.Many2one('res.branch', string='Unit Bisnis', required=True)
    branch_name = fields.Char('Business Unit', required=True)
    territory_id = fields.Many2one('res.territory', string='Area', required=True)
    territory_name = fields.Char('Territory Name', required=True)
    # department_id = fields.Many2one('hr.department', string='Sub Department', required=True)
    hrms_department_id = fields.Many2one(comodel_name='sanhrms.department', string='Departemen', store=True)
    department_name = fields.Char('Department Name', required=True)
    job_id = fields.Many2one('hr.job', string='Jabatan', required=True)
    job_name = fields.Char('Job Position', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True)
    contract_name = fields.Char('Referensi Kontrak', required=True)
    contract_number = fields.Char('Contract Number', required=True)
    mobile_phone = fields.Char('Contact Number', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    time_limit = fields.Integer('Time Limit (days)', required=True)
    notice_days = fields.Integer('Notice Days', required=True)
    start_notice = fields.Date('Start of Notice Period')
    rehire = fields.Boolean('Rehire', default=False)
    parent_id = fields.Many2one('parent.hr.employee', tracking=True, string='Atasan Langsung')
    contract_type_id = fields.Many2one('hr.contract.type', string='Tipe Kontrak')
    resource_calendar_id = fields.Many2one('resource.calendar', string='Jadwal Kerja')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                select
                id, 
                territory_id,
                territory_name,
                branch_id,
                branch_name,            
                hrms_department_id,
                department_name,
                employee_id,
                employee_name,
                nik_employee,
                parent_id,
                date_start,
                date_end,
                state,
                time_limit,
                rehire,
                company_id,
                company_name,
                emp_id,
                nik_lama,
                employee_address,
                status_employee,
                job_id,
                job_name,
                contract_id,
                contract_name,
                contract_number,
                mobile_phone,
                notice_days,
                contract_type_id,
                start_notice,
                resource_calendar_id
                from (
                SELECT
                    ROW_NUMBER() OVER (
                        ORDER BY
                        time_limit,
                        employee_id,
                        date_end,
                        contract_id
                    ) AS id, employee_id,
                            emp_id,
                            mobile_phone,
                            nik_employee,
                            coach_email,
                            parent_id,
                            coach_name,
                            nik_lama,
                            employee_name,
                            status_employee,
                            employee_address,
                            branch_id,
                            branch_name,
                            territory_id,
                            territory_name,
                            hrms_department_id,
                            department_name,
                            job_id,
                            job_name,
                            contract_id,
                            contract_name,
                            contract_number,
                            date_start,
                            date_end,
                            time_limit,
                            notice_days,
                            contract_type_id,
                            resource_calendar_id,
                            state,
                            start_notice,
                            rehire,
                            company_id,
                            company_name,
                            resignation_id FROM
                    (
                        SELECT
                        he.id AS employee_id,
                        he.employee_id as emp_id,
                        he.name AS employee_name,
                        he.mobile_phone AS mobile_phone,
                        he.nik AS nik_employee,
                        he2.id AS parent_id,
                        he2.name AS coach_name,
                        coalesce(he2.work_email, '') coach_email,
                        coalesce(he.nik_lama, he.nik) AS nik_lama,
                        he.employee_type AS status_employee,
                        concat(
                            he.private_street, ' ', he.private_street2,
                            ' ', he.private_city
                        ) AS employee_address,
                        rc.id AS company_id,
                        rc.name AS company_name,
                        rb.id AS branch_id,
                        rb.name AS branch_name,
                        rt.id AS territory_id,
                        rt.name AS territory_name,
                        hd.id AS hrms_department_id,
                        hd.name AS department_name,
                        hj.id AS job_id,
                        hj.name AS job_name,
                        hc2.id AS contract_id,
                        hc2.name AS contract_name,
                        hc2.number AS contract_number,
                        hc2.date_start AS date_start,
                        hc2.date_end AS date_end,
                        hc2.date_end - current_date AS time_limit,
                        hc2.notice_days,
                        hc2.contract_type_id,
                        hc2.resource_calendar_id,
                        hc2.state,
                        hres.id resignation_id,
                        hc2.date_end - (hc2.notice_days + 1) AS start_notice,
                        COALESCE(hel2.end_contract, FALSE) AS rehire
                        FROM
                        hr_employee he
                        INNER JOIN (
                            SELECT
                            MAX(id) AS id,
                            employee_id
                            FROM
                            hr_contract
                            where
                            state not in ('cancel', 'close', 'draft')
                            GROUP BY
                            employee_id
                        ) hc ON hc.employee_id = he.id
                        LEFT JOIN hr_employee he2 on he.parent_id = he2.id
                        LEFT JOIN hr_contract hc2 ON hc.id = hc2.id
                        AND hc.employee_id = he.id
                        LEFT JOIN res_company rc ON hc2.company_id = rc.id
                        LEFT JOIN res_branch rb ON hc2.branch_id = rb.id
                        LEFT JOIN res_territory rt ON hc2.area = rt.id
                        LEFT JOIN sanhrms_department hd ON hc2.hrms_department_id = hd.id
                        LEFT JOIN hr_job hj ON hc2.job_id = hj.id
                        LEFT JOIN (
                            SELECT
                            MAX(hel.id) AS id,
                            hel.employee_id
                            FROM
                            hr_employment_log hel
                            GROUP BY
                            hel.employee_id
                        ) hel ON hel.employee_id = he.id
                        LEFT JOIN hr_employment_log hel2 ON hel.id = hel2.id
                        and hel2.employee_id = he.id
                        left join hr_resignation hres on hres.employee_id = he.id
                        and hres.state not in ('cancel', 'inactive')
                        WHERE
                        hc2.active = TRUE
                        AND he.active = TRUE
                        AND he.state = 'approved'
                        AND (
                            hc2.date_end :: date BETWEEN current_date
                            AND current_date + INTERVAL '90 days'
                        )
                        and hres.id is null
                    ) AS emp) aa
        )
        """ % (self._table, ))

    def act_re_contract(self):
        # new_contract_id = self.new_contract('re-new',self.contract_id)
        return {
            'name': 'HR Contract Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',  # You can remove 'view_type' since it's optional and is not necessary in Odoo 17
            'res_model': 'hr.contract',
            'target': 'current',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,  # Ensure this XML ID is correct
            'context': {
                'default_company_id': self.company_id.id,
                'default_employee_id': self.employee_id.id,
                'default_date_start': self.date_end,
                'default_contract_type_id': self.contract_id.contract_type_id.id,
                'default_date_end': self.date_end + relativedelta(months=6),
                'default_resource_calendar_id': self.contract_id.resource_calendar_id.id,
                'default_type_id': self.contract_id.type_id.id,
                'default_job_id': self.contract_id.job_id.id,
                'depart_id': self.contract_id.depart_id.id,
                'default_state':'draft',
                'default_structure_type_id': self.contract_id.structure_type_id.id,
                'default_branch_id': self.branch_id.id,
                'default_area': self.contract_id.area.id,                
            },
        }
        
    def act_emp_finished(self):
        resign_id = self.env['hr.resignation'].sudo().create({
                'employee_id': self.employee_id.id,
                'emp_nos': self.employee_id.id,
                'employee_name': self.employee_id.name,
                'emp_nik': self.employee_id.nik,
                'area': self.territory_id.id,
                'branch_id': self.branch_id.id,
                'joined_date': self.employee_id.join_date,
                'resign_confirm_date': self.date_end,
                'submitted_date': self.date_end,
                'resignation_date': self.date_end,
                'effective_date': self.date_end,
                'expected_revealing_date': self.date_end,
                'reason':'End Of Contract',
                'notice_period':round(self.notice_days/30,1),
                'state':'draft',
                'resignation_type':'EOCT',
                'employee_contract':self.contract_id.name,
                })
        return {
            'name': 'HR Resignation Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.resignation',
            'res_id': resign_id.id,
            'target': 'current',
            'view_id': self.env.ref('hr_resignation.hr_resignation_view_form').id,
        }

    def act_promotion(self):
        new_contract_id = self.new_contract('re-new',self.contract_id)
        return {
            'name': 'HR Contract Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',  
            'res_model': 'hr.contract',
            'res_id': new_contract_id.id,  
            'target': 'current',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,
        }

    
    def new_contract(self,type,old_contract):
        new_status = old_contract.type_id.id
        for existing_contract in self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')]):
            existing_contract.state = 'close'
        if type == 'promotion' and (old_contract.structure_type_id.name != 'Employee' or old_contract.structure_type_id.name != 'Permanent' or old_contract.structure_type_id.name != 'Full-Time') :
            new_type = self.env['hr.contract.type'].search([('name','=','Permanent')])
            new_status = new_type.id
        else:
            new_status = old_contract.type_id.id
        month = datetime.now().month
        contracts_branch = self.env['hr.contract'].search([('name','ilike','/HC-'+str(self.territory_id.area_code)+'/'+str(self.branch_id.branch_code)+'/' +month_to_roman(month) + '/' + str(datetime.now().year))])
        number_contract = str(str('00000'+str(len(contracts_branch)+1))[3:])
        return self.env['hr.contract'].sudo().create({
                'company_id': old_contract.company_id.id,
                'employee_id': old_contract.employee_id.id,
                'date_start': old_contract.date_end,
                'contract_type_id': old_contract.contract_type_id.id,
                'date_end': old_contract.date_end + relativedelta(months=6),
                'name': number_contract+'/HC-'+str(self.territory_id.area_code)+'/'+str(self.branch_id.branch_code)+'/' +month_to_roman(month) + '/' + str(datetime.now().year),
                'resource_calendar_id': old_contract.resource_calendar_id.id,
                'type_id': new_status,
                'job_id': old_contract.job_id.id,
                'depart_id': old_contract.depart_id.id,
                'state':'draft',
                'structure_type_id': old_contract.structure_type_id.id,
                'branch_id': old_contract.branch_id.id,
                'area': old_contract.area.id,
                })
        
    def act_deactive_employee(self):
        for line in self.env['hr.employee.contract.monitoring']:
            if line.date_end <= datetime.today() + timedelta(days=7) and not line.rehire:
                line.employee_id.state = 'inactive'
                line.employee_id.active = False
                line.contract_id.state = 'close'
                   
    def mail_send_hr(self):
        # try:
            today_date = fields.Datetime.today().date()
            today = self._format_date(today_date)
            query_superior_id = """ 
                    SELECT DISTINCT hcm.branch_id FROM hr_employee_contract_monitoring hcm where hcm.time_limit <= 90;
                """
            self.env.cr.execute(query_superior_id)
            # users = 'azizah <azizah_nurmahdyah@sanbe-farma.com>'    
            # users = ''    
            for distinct_records in self.env.cr.dictfetchall():
                branch_id = self.env['res.branch'].browse(distinct_records['branch_id'])
                list_email = self.env['hr.mail.config'].search([('branch_id', '=', distinct_records['branch_id'])])
                # email_list = [rec.list_email for rec in list_email if rec.list_email]
                # users = ', ' + str(list_email.list_email or '')
                # users = users + ', ' + ', '.join(filter(None, list_email.mapped('list_email'))) 
                users = ', '.join(filter(None, list_email.mapped('list_email')))                 
                table_rows = ""
                idx = 1
                for records in self.env['hr.employee.contract.monitoring'].search([('branch_id', '=', distinct_records['branch_id']),('time_limit','<=',90)]):
                    table_rows += f"""
                    <tr>
                        <td>{idx}</td> 
                        <td>{records.nik_employee}</td>
                        <td>{records.employee_name}</td>
                        <td>{records.branch_id.name}</td>
                        <td>{records.job_id.name}</td>
                        <td>{records.department_id.name}</td>
                        <td>{records.company_id}</td>
                        <td>{self._format_date(records.date_start)}</td>
                        <td>{self._format_date(records.date_end)}</td>
                        <td>{self._get_duration(records)}</td>
                    </tr>
                    """
                    idx += 1
                table_header_template = table_header.format(
                                today=today,
                                branch=branch_id.name,
                            )                        
                email_body = f"""<p>Kepada Yth.</p>
                <p>Personalia PT Sanbe Farma <br/>
                di Tempat</p>
                {table_header_template}
                {table_rows}
                {table_footer}
                <p>Odoo - ERP <br/> PT Sanbe Farma</p>
                """                    
                email = self.env.ref('sanbe_hr_monitoring_contract.email_template_reminder_contract_end')
                email_dict = {'subject':f"""Pengingat HR: Kontrak Karyawan yang Akan Berakhir""",
                                'email_to': users,
                                'email_from': 'System Administrator <donotreply@sanbe-farma.com>',
                                'body_html': email_body,
                                }
                # raise UserError('Test')
                email.sudo().write(email_dict)
                email.with_context().send_mail(self.id,force_send=True)
                print('Kirim ke HR')


    def _get_duration(self, contract):
        if not contract.date_start or not contract.date_end:
            return ''

        today = fields.Datetime.today().date()
        duration = contract.date_end - today
        total_days = duration.days

        years = total_days // 365
        remaining_days = total_days % 365
        months = remaining_days // 30
        days = remaining_days % 30

        result = []
        if years and total_days >= 365:
            result.append(f"{years} tahun")
        if months:
            result.append(f"{months} bulan")
        if days or not result:
            result.append(f"{days} hari")

        return ' '.join(result)
    
    def _format_date(self, record):
        if not record:
            return '-'
        day = record.strftime('%d')
        month = bulan_map[record.strftime('%m')]
        year = record.strftime('%Y')
        return f"{day} {month} {year}"

        
class HrContractMonitoring(models.Model):
    _name = 'hr.contract.monitoring'
    _description = 'Hr Contract Monitoring'
    _inherit =['mail.thread']

    name = fields.Char('Name', default=lambda self: self._generate_name())
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    employee_name = fields.Char('Employee Name', related='employee_id.name', readonly=True, store=True)
    nik_employee = fields.Char('Employee NIK', related='employee_id.nik', readonly=True, store=True)
    #superior_id = fields.Many2one('parent.hr.employee', 'Immediate Superior', related='employee_id.parent_id', readonly=True, store=True)
    superior_id = fields.Many2one('hr.employee', 'Immediate Superior', related='employee_id.parent_id', readonly=True, store=True)
    nik_lama = fields.Char('Old NIK', related='employee_id.nik_lama', readonly=True, store=True)
    address_id = fields.Many2one('res.partner',related='employee_id.address_id',string='Partner')
    employee_address = fields.Char('Address')
    employee_private_street = fields.Char('Street', related='employee_id.private_street', readonly=True, store=True)
    employee_private_street2 = fields.Char('Street', related='employee_id.private_street2', readonly=True, store=True)
    employee_private_city = fields.Char('City', related='employee_id.private_city', readonly=True, store=True)
    status_employee = fields.Char(string='Employee Status', readonly=True, store=True)
    company_id = fields.Many2one('res.company', related='employee_id.company_id', string='Company', readonly=True, store=True)
    company_name = fields.Char('Company Name', related='company_id.name', readonly=True, store=True)
    branch_id = fields.Many2one('res.branch', related='employee_id.branch_id', string='Business Unit', readonly=True, store=True)
    branch_name = fields.Char(related='branch_id.name', string='Business Unit', readonly=True, store=True)
    territory_id = fields.Many2one('res.territory', related='employee_id.area', string='Area', readonly=True, store=True)
    territory_name = fields.Char(related='territory_id.name', string='Area', readonly=True, store=True)
    # department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Sub Department', readonly=True, store=True)
    hrms_department_id = fields.Many2one(comodel_name='sanhrms.department', related='employee_id.hrms_department_id', string='Departemen', store=True)
    department_name = fields.Char(related='hrms_department_id.name', string='Departemen', readonly=True, store=True)
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', readonly=True, store=True)
    job_name = fields.Char(string='Job Position', related='job_id.name', readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True, store=True)
    contract_number = fields.Char('Contract Number', related='contract_id.number', readonly=True, store=True)
    mobile_phone = fields.Char('Contact Number', related='employee_id.mobile_phone', readonly=True, store=True)
    date_start = fields.Date('Start Date', related='employee_id.contract_id.date_start', readonly=True, store=True)
    date_end = fields.Date('End Date', related='employee_id.contract_id.date_end', readonly=True, store=True)
    notice_days = fields.Integer('Notice Days', related='contract_id.notice_days', readonly=True, store=True)
    rehire = fields.Boolean('Rehire', default=False, store=True)
    new_contract_id = fields.Many2one('hr.contract','New Contract', store=True)
    employee_exit_id = fields.Many2one('hr.resignation','Emloyee Exit', store=True)
    is_done = fields.Selection([('waiting', 'Waiting'), ('done', 'Done')], 'Processed', default='waiting', store=True)
    time_limit = fields.Integer('Time Limit (days)', compute="_waiting_expired")
    result = fields.Selection([('re-new', 'Re Contract'), ('eof', 'Employee Exit'), ('promotion', 'Promotion')],
                            'Processed', default='eof')
    state = fields.Selection(related="contract_id.state", string='Status', store=True)


    _sql_constraints = [
        ('name_monitoring_uniq', 'unique (name)', "Just Once time Proccess")
    ]

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        
        branch_ids_from_context = self.env.context.get('allowed_branch_ids')
        
        if branch_ids_from_context:
            if not branch_ids_from_context:
                branch_ids_to_filter = [0]
            else:
                branch_ids_to_filter = branch_ids_from_context

            args = [('branch_id', 'in', branch_ids_to_filter)] + list(args)

        else:
            allowed_company_ids = self.env.context.get('allowed_company_ids')

            if allowed_company_ids:
                company_branches = self.env['res.branch'].sudo().search([
                    ('company_id', 'in', allowed_company_ids)
                ])

                branch_ids_from_switcher = company_branches.ids

                if not branch_ids_from_switcher:
                    branch_ids_from_switcher = [0]

                args = [('branch_id', 'in', branch_ids_from_switcher)] + list(args)
    
            else:
                _logger.info("[_search] Tidak ada filter cabang dinamis diterapkan dari konteks.")

        return super(HrContractMonitoring, self)._search(args, offset, limit, order, count)


    def waiting_expired(self):
        for line in self:
            if line.employee_id:
                wait_expired = line.date_end - fields.Datetime.today()
                days_left = wait_expired.days
                return days_left
    
    def _generate_name(self):
        for line in self:
            if line.employee_id:
                name = str(fields.Datetime.today().year)[-2:] + ('0' + str(fields.Datetime.today().month))[-2:] + line.employee_id.nik
                return name
            
    @api.onchange('employee_id')
    def _generate_address(self):
        for line in self:
            if line.employee_id:
                address = f"{line.employee_id.private_street or line.employee_id.address_id.street} s{line.employee_id.private_street2} {line.employee_id.private_city}"
                line.employee_address = address
                
    def generate_address(self, employee):
        if employee:
            personal = self.env['hr.employee'].browse(employee.id)
            address = f"{personal.private_street  or employee.address_id.street} {personal.private_street2} {personal.private_city}"
            return address
    
    def generate_data(self):
        # if datetime.today().day == 20:
            for employee in self.env['hr.employee'].search([]):
                start_date = datetime.today().strftime("%Y-%m-20")
                end_date = (datetime.today().replace(day=1) + relativedelta(months=1) - timedelta(days=1)).strftime("%Y-%m-%d")
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', employee.id),
                    ('date_end', '>=', start_date),
                    ('date_end', '<=', end_date)
                ], limit=1, order='date_end desc')
                rehire = self.env['hr.employment.log'].search([
                    ('employee_id', '=', employee.id)
                ], limit=1, order='id desc').end_contract
                if contract:
                    self.env['hr.contract.monitoring'].sudo().create({
                        'name': str(fields.Datetime.today().year)[-2:] + ('0' + str(fields.Datetime.today().month))[-2:] + employee.nik,
                        'employee_id': employee.id,
                        'contract_id': contract.id,
                        'rehire': rehire,
                        'is_done': 'waiting',
                    })
                # _logger.info('Cron Job Finished')
            
        
    def act_re_contract(self):
        if self.is_done != 'done':
            self.is_done = 'done'
            self.result = 're-new'
            self.new_contract('re-new',self.contract_id)
        return {
            'name': 'HR Contract Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',  # You can remove 'view_type' since it's optional and is not necessary in Odoo 17
            'res_model': 'hr.contract',
            'res_id': self.new_contract_id.id,  # Make sure new_contract is a valid record
            'target': 'current',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,  # Ensure this XML ID is correct
        }
        
    def act_emp_finished(self):
        if self.is_done != 'done':
            self.is_done = 'done'
            self.result = 'eof'
            resign_id = self.env['hr.resignation'].sudo().create({
                    'employee_id': self.employee_id.id,
                    'resign_confirm_date': fields.Datetime.today(),
                    'expected_revealing_date': self.date_end,
                    'reason':'End Of Contract',
                    'notice_period':self.notice_days,
                    'state':'draft',
                    'resignation_type':'EOCT',
                    'employee_contract':self.contract_id.name,
                    })
            self.employee_exit_id = resign_id.id
        return {
            'name': 'HR Resignation Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.resignation',
            'res_id': self.employee_exit_id.id,
            'target': 'current',
            'view_id': self.env.ref('hr_resignation.hr_resignation_view_form').id,
        }

    def act_promotion(self):
        if self.is_done != 'done':
            self.is_done = 'done'
            self.result = 'promotion'
            self.new_contract('promotion',self.contract_id)
        return {
            'name': 'HR Contract Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',  # You can remove 'view_type' since it's optional and is not necessary in Odoo 17
            'res_model': 'hr.contract',
            'res_id': self.new_contract_id.id,  # Make sure new_contract is a valid record
            'target': 'current',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,  # Ensure this XML ID is correct
        }
    
    def new_contract(self,type,old_contract):
        new_status = old_contract.type_id.id
        if type == 'promotion' and (old_contract.structure_type_id.name != 'Employee' or old_contract.structure_type_id.name != 'Permanent' or old_contract.structure_type_id.name != 'Full-Time') :
            new_type = self.env['hr.contract.type'].search([('name','=','Permanent')])
            new_status = new_type.id
        else:
            new_status = old_contract.type_id.id
        month = datetime.now().month  # March (3rd month)
        contracts_branch = self.env['hr.contract'].search([('name','ilike','HC'+str(self.territory_id.area_code)+'/'+str(self.branch_id.branch_code)+'/' +month_to_roman(month) + '/' + str(datetime.now().year))])
        number_contract = str(str('00000'+str(len(contracts_branch)+1))[3:])        
        new_contract = self.env['hr.contract'].sudo().create({
                'company_id': old_contract.company_id.id,
                'employee_id': old_contract.employee_id.id,
                'date_start': old_contract.date_end,
                'date_end': old_contract.date_end + relativedelta(months=6),
                'name': number_contract+'/HC-'+str(self.territory_id.area_code)+'/'+str(self.branch_id.branch_code)+'/' +month_to_roman(month) + '/' + str(datetime.now().year),
                'resource_calendar_id': old_contract.resource_calendar_id.id,
                'type_id': new_status,
                'job_id': old_contract.job_id.id,
                'depart_id': old_contract.depart_id.id,
                'state':'draft',
                'structure_type_id': old_contract.structure_type_id.id,
                'branch_id': old_contract.branch_id.id,
                'area': old_contract.area.id,
                })
        self.new_contract_id = new_contract.id

        
            
    def mail_send_hr(self):
        # try:
            list_employe_contract = self.env['hr.contract.monitoring'].search([('is_done','=','waiting'),('company_id','=',self.company_id.id)])
            distinct_records = []
            for branch_id, group in groupby(list_employe_contract, key=lambda r: r.branch_id.id):
                distinct_records.append(next(group)) 
                users = 'azizah <azizah_nurmahdyah@sanbe-farma.com>'        
                for record in distinct_records:
                    query = """ SELECT hcm.id,
                            rb.name AS branch_name,
                            rt.name AS territory_name,
                            sd.id AS hrms_department_id,
                            sd.name::VARCHAR AS department_name,   -- Single-language field for department
                            hj.id AS job_id,
                            hj.name::VARCHAR AS job_name,          -- Single-language field for job
                            he.name parent_name,
                            hcm.employee_name,
                            hc.date_end::date date_end
                        FROM 
                            hr_contract_monitoring hcm
                        LEFT JOIN 
                            res_branch rb ON hcm.branch_id = rb.id
                        LEFT JOIN 
                            res_territory rt ON hcm.territory_id = rt.id
                        LEFT JOIN 
                            sanhrms_department sd ON hcm.hrms_department_id = sd.id
                        LEFT JOIN 
                            hr_job hj ON hj.id = hcm.job_id
                        LEFT JOIN 
                            hr_employee he ON he.id = hcm.superior_id
                        LEFT JOIN 
                            hr_contract hc ON hc.id = hcm.contract_id
                        WHERE 
                            hcm.is_done = 'waiting' and hcm.branch_id = %s """
                    self.env.cr.execute((query) % (record.branch_id.id))
                    list_email = self.env['hr.mail.config'].search([('branch_id', '=', record.branch_id.id)])
                    users = users +', '+ str(list_email.list_email or '')                    
                    table_rows = ""
                    for record in self.env.cr.dictfetchall():
                        job_name = self.env['hr.contract.monitoring'].browse(record['id']).job_name
                        department_name = self.env['hr.contract.monitoring'].browse(record['id']).department_name
                        table_rows += f"""
                        <tr>
                            <td>{record['territory_name']}</td>
                            <td>{record['branch_name']}</td>
                            <td>{department_name}</td>
                            <td>{record['employee_name']}</td>
                            <td>{job_name}</td>
                            <td>{record['parent_name'] or ''}</td>
                            <td>{record['date_end']}</td>
                        </tr>
                        """                        
                    email_body = f"""
                    <<p>Semangat Pagi <br/>
                    Tim Human Resource,</p>
                    {table_header}
                    {table_rows}
                    {table_footer}
                    <p>Admin Sistem</p>
                    """                    
                    email = self.env.ref('sanbe_hr_monitoring_contract.email_template_reminder_contract_end')
                    email_dict = {'subject':f"""Pengingat HR: Kontrak Karyawan yang Akan Berakhir""",
                                    'email_to': users,
                                    'email_from': 'System Administrator <donotreply@sanbe-farma.com>',
                                    'body_html': email_body,
                    
                                    }
                    # raise UserError('Test')
                    email.sudo().write(email_dict)
                    email.with_context().send_mail(self.id, force_send=True)
                    print('Kirim ke HR')        
        # except Exception as e:
        #     _logger.error("Error in mail_send_mentor cron job: %s", e)
    
    def mail_send_mentor(self):
        # try:

            query_superior_id = """ select distinct he.parent_id superior_id, 
                                        he.name mentor_name, 
                                        coalesce(he2.work_email,'') work_email 
                                    from 
                                        hr_contract_monitoring hcm 
                                    left join 
                                        hr_employee he on hcm.employee_id = he.id 
                                    left join 
                                        hr_employee he2 on he.parent_id = he2.id 
                                    where 
                                        hcm.is_done = 'waiting' and he.parent_id is not null"""
            self.env.cr.execute(query_superior_id)                 
            for data_superiors in self.env.cr.dictfetchall():
                users = 'azizah <azizah_nurmahdyah@sanbe-farma.com>,' + data_superiors['work_email']
                query = """ SELECT hcm.id,
                        rb.name AS branch_name,
                        rt.name AS territory_name,
                        sd.id AS hrms_department_id,
                        sd.name::VARCHAR AS department_name,   -- Single-language field for department
                        hj.id AS job_id,
                        hj.name::VARCHAR AS job_name,          -- Single-language field for job
                        he.name parent_name,
                        hcm.employee_name,
                        hc.date_end::date date_end
                    FROM 
                        hr_contract_monitoring hcm
                    LEFT JOIN 
                        res_branch rb ON hcm.branch_id = rb.id
                    LEFT JOIN 
                        res_territory rt ON hcm.territory_id = rt.id
                    LEFT JOIN 
                        sanhrms_department sd ON hcm.hrms_department_id = sd.id
                    LEFT JOIN 
                        hr_job hj ON hj.id = hcm.job_id
                    LEFT JOIN 
                        hr_employee he ON he.id = hcm.superior_id
                    LEFT JOIN 
                        hr_contract hc ON hc.id = hcm.contract_id
                    WHERE 
                        hcm.is_done = 'waiting' and hcm.superior_id = %s """
                self.env.cr.execute((query) % (data_superiors['superior_id']))
                table_rows = ""
                mentor_name = ""
                for record in self.env.cr.dictfetchall():
                    job_name = self.env['hr.contract.monitoring'].browse(record['id']).job_name
                    department_name = self.env['hr.contract.monitoring'].browse(record['id']).department_name
                    mentor_name = record['parent_name']
                    table_rows += (("""
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
                    """    )%(record['territory_name'],record['branch_name'],department_name,record['employee_name'],job_name,record['parent_name'] or '',record['date_end']))
                email_body = (("""
                <p>Semangat Pagi <br/>
                Mentor/Supervisor %s </p> %s %s %s  <p>Human Resource</p>""")%(mentor_name,table_header,table_rows,table_footer))
                email = self.env.ref('sanbe_hr_monitoring_contract.email_template_reminder_contract_end')
                email_dict = {'subject':'Pengingat: Kontrak Karyawan yang Akan Berakhir',
                                'email_to': users,
                                'email_from': 'Human Resource <donotreply@sanbe-farma.com>',
                                'body_html': email_body,
                
                                }
                email.sudo().write(email_dict)
                email.with_context().send_mail(self.id, force_send=True)
    #             print('Kirim ke Mentor')
        # except Exception as e:
        #     _logger.error("Error in mail_send_mentor cron job: %s", e)
