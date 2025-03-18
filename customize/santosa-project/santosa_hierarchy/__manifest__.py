# -*- coding: utf-8 -*-
{
    'name': "Santosa HRMS",

    'summary': """
        Module Santosa HRMS""",

    'description': """
        Manajemen HRMS Santosa
    """,

    'author': "Febry Ramadhan",
    'website': "https::/sanbe.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','mail','base_territory','hr','hr_contract','hr_employee_updation','hr_payroll_community', 'hr_payroll_account_community'],

		# Include ALL XML Code in Here be mindful of order
    'data': [
        # 'security/access_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/documents/hr_employee_document.views.xml',
        'views/employee/hr_employee.views.xml',
        'views/employee/hr_employment.xml',
        'views/employee/hr_employment_tracking.xml',
        'views/employee/hr_checking_id.xml',
        # 'views/payroll/hr_payroll_menu.xml',
        'views/payroll/hr_payroll_entry.xml',
        'views/employee/hr_employee_mutation.xml',
        'views/branch/res_branch.xml',
        'views/area/area.views.xml',
        'views/contract/hr_contract.views.xml',
        'views/warning_letter/hr_warning_letter.views.xml',
        'views/warning_letter/hr_warning_letter_type.views.xml',
        # 'views/contract/hr_contract_hide.views.xml',

        'views/hierarchy/hierarchy_menuitem.xml',
        'views/employee_exit/employee_exit.views.xml',
        'views/documents/hr_menu_item.xml',
        'views/master_data/directorate/directorate.views.xml',
        'views/master_data/division/division.views.xml',
        'views/master_data/department/department.views.xml',
        'views/master_data/employee_status/hr_emp_status.views.xml',
        'views/master_data/employee_level/employee_level.views.xml',
        'views/master_data/document_type/document_type.views.xml',

        'views/documents/hr_document.views.xml',
        'wizards/hr_monitoring_contract.xml',

        # 'views/master.views.xml',

        'views/personal_adm_menuitem.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 'inventory_laptop/static/src/css/custom_style.css',
            # 'sidb/static/src/scss/profildesa.scss',
        ],
    },
    

    'installable': True,
    'application': True,
    'auto_install': False

}