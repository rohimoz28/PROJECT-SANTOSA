from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class HrResignation(models.Model):
    _inherit = 'hr.resignation'
    #_check_company_auto = True

    branch_id = fields.Many2one('res.branch', string="Branch")
    # branch_ids = self.env.user.branch_ids.ids  # Ambil branch yang diizinkan untuk user
    # resignations = self.env['hr.resignation'].search([('branch_id', 'in', branch_ids)])
    # print(resignations)


    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(HrResignation, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'search':
    #         branch_ids = self.env['res.branch'].search([('company_id', 'in', self.env.user.company_ids.ids)]).ids
    #         _logger.info(f"Branch IDs for domain: {branch_ids}")
    #         if 'branch_id' in res.get('fields', {}):
    #             res['fields']['branch_id']['domain'] = [('id', 'in', branch_ids)]
    #     return res
    

    
    @api.model
    def get_dashboard_data(self, month_name='defaut'):
        
        resignation_query = """
            WITH months AS (
    SELECT
        gs.month_num,
        TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
    FROM 
        generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
),
area_months AS (
    SELECT 
        rt.id AS area_id,
        rt.name AS area_name,
        m.month_num,
        m.month_name
    FROM 
        res_territory rt
    CROSS JOIN 
        months m
    WHERE 
        rt.name NOT IN ('Sanbe Farma Group')
)
SELECT 
    am.month_name AS month,
    am.area_name AS areas,
    COALESCE(COUNT(hr.resign_confirm_date), 0) AS resignation_count
FROM 
    area_months am
LEFT JOIN 
    hr_resignation hr
ON 
    am.area_id = hr.area 
    AND am.month_num = EXTRACT(MONTH FROM hr.resign_confirm_date)
    AND hr.state = 'approved'
    AND hr.resign_confirm_date IS NOT NULL
    AND hr.resignation_type = 'RESG'
GROUP BY 
    am.month_name, am.month_num, am.area_name
ORDER BY 
    am.month_num, am.area_name;

        """
        end_contract_query = """
            WITH months AS (
    SELECT
        gs.month_num,
        TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
    FROM 
        generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
),
area_months AS (
    SELECT 
        rt.id AS area_id,
        rt.name AS area_name,
        m.month_num,
        m.month_name
    FROM 
        res_territory rt
    CROSS JOIN 
        months m
    WHERE 
        rt.name NOT IN ('Sanbe Farma Group')
)
SELECT 
    am.month_name AS month,
    am.area_name AS areas,
    COALESCE(COUNT(hr.resign_confirm_date), 0) AS resignation_count
FROM 
    area_months am
LEFT JOIN 
    hr_resignation hr
ON 
    am.area_id = hr.area 
    AND am.month_num = EXTRACT(MONTH FROM hr.resign_confirm_date)
    AND hr.state = 'approved'
    AND hr.resign_confirm_date IS NOT NULL
    AND hr.resignation_type = 'EOCT'
GROUP BY 
    am.month_name, am.month_num, am.area_name
ORDER BY 
    am.month_num, am.area_name;

        """

        transfer_to_group_query = """
            WITH months AS (
    SELECT
        gs.month_num,
        TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
    FROM 
        generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
),
area_months AS (
    SELECT 
        rt.id AS area_id,
        rt.name AS area_name,
        m.month_num,
        m.month_name
    FROM 
        res_territory rt
    CROSS JOIN 
        months m
    WHERE 
        rt.name NOT IN ('Sanbe Farma Group')
)
SELECT 
    am.month_name AS month,
    am.area_name AS areas,
    COALESCE(COUNT(hr.resign_confirm_date), 0) AS resignation_count
FROM 
    area_months am
LEFT JOIN 
    hr_resignation hr
ON 
    am.area_id = hr.area 
    AND am.month_num = EXTRACT(MONTH FROM hr.resign_confirm_date)
    AND hr.state = 'approved'
    AND hr.resign_confirm_date IS NOT NULL
    AND hr.resignation_type = 'TFTG'
GROUP BY 
    am.month_name, am.month_num, am.area_name
ORDER BY 
    am.month_num, am.area_name;


"""

        terminate_query = """
            WITH months AS (
    SELECT
        gs.month_num,
        TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
    FROM 
        generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
),
area_months AS (
    SELECT 
        rt.id AS area_id,
        rt.name AS area_name,
        m.month_num,
        m.month_name
    FROM 
        res_territory rt
    CROSS JOIN 
        months m
    WHERE 
        rt.name NOT IN ('Sanbe Farma Group')
)
SELECT 
    am.month_name AS month,
    am.area_name AS areas,
    COALESCE(COUNT(hr.resign_confirm_date), 0) AS resignation_count
FROM 
    area_months am
LEFT JOIN 
    hr_resignation hr
ON 
    am.area_id = hr.area 
    AND am.month_num = EXTRACT(MONTH FROM hr.resign_confirm_date)
    AND hr.state = 'approved'
    AND hr.resign_confirm_date IS NOT NULL
    AND hr.resignation_type = 'TERM'
GROUP BY 
    am.month_name, am.month_num, am.area_name
ORDER BY 
    am.month_num, am.area_name;

            """
        
        pension_query = """
            WITH months AS (
    SELECT
        gs.month_num,
        TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
    FROM 
        generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
),
area_months AS (
    SELECT 
        rt.id AS area_id,
        rt.name AS area_name,
        m.month_num,
        m.month_name
    FROM 
        res_territory rt
    CROSS JOIN 
        months m
    WHERE 
        rt.name NOT IN ('Sanbe Farma Group')
)
SELECT 
    am.month_name AS month,
    am.area_name AS areas,
    COALESCE(COUNT(hr.resign_confirm_date), 0) AS resignation_count
FROM 
    area_months am
LEFT JOIN 
    hr_resignation hr
ON 
    am.area_id = hr.area 
    AND am.month_num = EXTRACT(MONTH FROM hr.resign_confirm_date)
    AND hr.state = 'approved'
    AND hr.resign_confirm_date IS NOT NULL
    AND hr.resignation_type = 'RETR'
GROUP BY 
    am.month_name, am.month_num, am.area_name
ORDER BY 
    am.month_num, am.area_name;

"""
        self.env.cr.execute(resignation_query)
        resignation_data = self.env.cr.dictfetchall()
        # _logger.info("End Resignation Data: %s", resignation_data)
        
        self.env.cr.execute(end_contract_query)
        end_contract_data = self.env.cr.dictfetchall()
        # _logger.info("End Contract Data: %s", end_contract_data)

        self.env.cr.execute(transfer_to_group_query)
        transfer_to_group = self.env.cr.dictfetchall()
        # _logger.info("Transfer Group Data: %s", transfer_to_group)

        self.env.cr.execute(terminate_query)
        terminate_data = self.env.cr.dictfetchall()
        # _logger.info("Terminate Data: %s", terminate_data)

        self.env.cr.execute(pension_query)
        pension_data = self.env.cr.dictfetchall()
        # _logger.info("Terminate Data: %s", pension_data)

        return {
            'resignation_data': resignation_data,
            'end_contract_data': end_contract_data,
            'transfer_to_group': transfer_to_group,
            'terminate_data': terminate_data,
            'pension_data': pension_data
        }
    
    @api.model
    def get_employee_data(self, month_name='defaut'):
        
        employee_active_query = """
            WITH months AS (
            SELECT
                gs.month_num,
                TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
            FROM 
                generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
        ),
        area_months AS (
            SELECT 
                rt.id AS area_id,
                rt.name AS area_name,
                m.month_num,
                m.month_name
            FROM 
                res_territory rt 
            CROSS JOIN 
                months m
            WHERE 
                rt.name NOT IN ('Sanbe Farma Group') and ID <> 5
                )           
        SELECT 
            am.month_name AS month,
            am.area_name AS areas,
            COALESCE(COUNT(he.employee_id), 0) AS employee_count
        FROM 
            area_months am
        LEFT JOIN 
            hr_employee he
        ON 
            am.area_id = he.area 
            AND he.emp_status IN ('confirmed', 'probation')
            where active = true
        GROUP BY 
            am.month_name, am.month_num, am.area_name
        ORDER BY 
            am.month_num, am.area_name;
        """

        employee_exit_query = """
            WITH months AS (
            SELECT
                gs.month_num,
                TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
            FROM 
                generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
        ),
        area_months AS (
            SELECT 
                rt.id AS area_id,
                rt.name AS area_name,
                m.month_num,
                m.month_name
            FROM 
                res_territory rt
            CROSS JOIN 
                months m
            WHERE 
                rt.name NOT IN ('Sanbe Farma Group')
        )
        SELECT 
            am.month_name AS month,
            am.area_name AS areas,
            COALESCE(
                COUNT(hr.id), 
                0
            ) AS employee_count
        FROM 
            area_months am
        LEFT JOIN 
            hr_resignation hr
        ON 
            am.area_id = hr.area 
            AND am.month_num = EXTRACT(MONTH FROM hr.resign_confirm_date)
            AND hr.state = 'approved'
            AND EXTRACT(YEAR FROM hr.resign_confirm_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        LEFT JOIN 
            hr_employee he
        ON 
            hr.employee_id = he.id
        WHERE 
            hr.resign_confirm_date IS NULL 
            OR EXTRACT(YEAR FROM hr.resign_confirm_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY 
            am.month_name, 
            am.month_num, 
            am.area_name
        ORDER BY 
            am.month_num, 
            am.area_name;

        """

        employee_new_query = """
            WITH months AS (
            SELECT
                gs.month_num,
                TO_CHAR(DATE '2024-01-01' + (gs.month_num - 1) * INTERVAL '1 month', 'Mon') AS month_name
            FROM 
                generate_series(1, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER) AS gs(month_num)
        ),
        area_months AS (
            SELECT 
                rt.id AS area_id,
                rt.name AS area_name,
                m.month_num,
                m.month_name
            FROM 
                res_territory rt
            CROSS JOIN 
                months m
            WHERE 
                rt.name NOT IN ('Sanbe Farma Group')
        )
        SELECT 
            am.month_name AS month,
            am.area_name AS areas,
            COALESCE(
                COUNT(he.employee_id),
                0
            ) AS employee_count
        FROM 
            area_months am
        LEFT JOIN 
            hr_employee he
        ON 
            am.area_id = he.area 
            AND am.month_num = EXTRACT(MONTH FROM he.join_date)
            AND EXTRACT(YEAR FROM he.join_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            AND he.emp_status IN ('confirmed', 'probation')
            AND he.active IS true
            GROUP BY 
                    am.month_name, am.month_num, am.area_name
        ORDER BY 
            am.month_num, 
            am.area_name;

        """
        
        self.env.cr.execute(employee_active_query)
        employee_active_data = self.env.cr.dictfetchall()
        _logger.info("Employee active: %s", employee_active_data)

        self.env.cr.execute(employee_exit_query)
        employee_exit_data = self.env.cr.dictfetchall()
        _logger.info("Employee exit: %s", employee_exit_data)

        self.env.cr.execute(employee_new_query)
        employee_new_data = self.env.cr.dictfetchall()
        _logger.info("Employee new: %s", employee_new_data)

        return {
            'employee_active_data': employee_active_data,
            'employee_exit_data': employee_exit_data,
            'employee_new_data': employee_new_data
        }
    
    