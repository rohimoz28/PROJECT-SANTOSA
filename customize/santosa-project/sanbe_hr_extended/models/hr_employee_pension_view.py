from odoo import fields, models, tools, api


class HrEmployeePensionView(models.Model):
    _auto = False
    _name = 'hr.employee.pension.view'
    _description = 'HR Employee View SQL'
    _order = 'name'

    id = fields.Integer(string='ID', required=True)
    name = fields.Char(string='Nama Karyawan')
    employee_id = fields.Char(string='ID Karyawan')
    nik = fields.Char(string='NIK')
    job_id = fields.Many2one('hr.job', string='Jabatan')
    birthday = fields.Date(string='Tanggal Lahir')
    retire_age = fields.Integer('Usia Pensiun', default=55)
    join_date = fields.Date(string='Join Date')
    job_status = fields.Selection([('permanent', 'Karyawan Tetap (PKWTT)'),
                                   ('contract', 'Karyawan Kontrak (PKWT)'),
                                   ('partner_doctor', 'Dokter Mitra'),
                                   ('visitor', 'Visitor'),
                                   ], string='Status Hubungan Kerja')
    pension_date = fields.Date(string='Tanggal Pensiun')
    pension_state = fields.Selection([
        ('running', 'Running'),
        ('expired', 'Expired')],
        string='Status Pensiun'
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                e.id as id,                                                 
                e.name as name,
                e.employee_id,
                e.nik,                        
                e.job_id,               
                e.birthday,                 
                e.retire_age,                
                e.join_date,
                e.job_status,                 
                MAKE_DATE(
                    (EXTRACT(YEAR FROM e.birthday)::int + e.retire_age),
                    EXTRACT(MONTH FROM e.birthday)::int,
                    LEAST(
                        EXTRACT(DAY FROM e.birthday)::int,
                        EXTRACT(
                            DAY FROM
                            (
                                DATE_TRUNC(
                                    'month',
                                    MAKE_DATE(
                                        (EXTRACT(YEAR FROM e.birthday)::int + e.retire_age),
                                        EXTRACT(MONTH FROM e.birthday)::int,
                                        1
                                    )
                                ) + INTERVAL '1 month - 1 day'
                            )
                        )::int
                    )
                )::date AS pension_date,
                /* pension_state */
                CASE
                    WHEN CURRENT_DATE <
                        MAKE_DATE(
                            (EXTRACT(YEAR FROM e.birthday)::int + e.retire_age),
                            EXTRACT(MONTH FROM e.birthday)::int,
                            LEAST(
                                EXTRACT(DAY FROM e.birthday)::int,
                                EXTRACT(
                                    DAY FROM
                                    (
                                        DATE_TRUNC(
                                            'month',
                                            MAKE_DATE(
                                                (EXTRACT(YEAR FROM e.birthday)::int + e.retire_age),
                                                EXTRACT(MONTH FROM e.birthday)::int,
                                                1
                                            )
                                        ) + INTERVAL '1 month - 1 day'
                                    )
                                )::int
                            )
                        )::date
                    THEN 'running'
                    ELSE 'expired'
                END AS pension_state
            FROM hr_employee e
            WHERE
            e.birthday IS NOT NULL
            AND e.retire_age IS NOT NULL
            /* FILTER: HANYA YANG RUNNING */
            AND CURRENT_DATE <
                MAKE_DATE(
                    (EXTRACT(YEAR FROM e.birthday)::int + e.retire_age),
                    EXTRACT(MONTH FROM e.birthday)::int,
                    LEAST(
                        EXTRACT(DAY FROM e.birthday)::int,
                        EXTRACT(
                            DAY FROM
                            (
                                DATE_TRUNC(
                                    'month',
                                    MAKE_DATE(
                                        (EXTRACT(YEAR FROM e.birthday)::int + e.retire_age),
                                        EXTRACT(MONTH FROM e.birthday)::int,
                                        1
                                    )
                                ) + INTERVAL '1 month - 1 day'
                            )
                        )::int
                    )
                )::date
            )
        """ % (self._table, ))
