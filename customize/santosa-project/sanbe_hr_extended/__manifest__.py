{
    'name': "Santosa HR Extended",

    'summary': "Santosa HR Extended",

    'description': """
   Santosa HR Extended
    """,

    'author': "Albertus Restiyanto Pramayudha",
    'website': "http://www.yourcompany.com",
    "support": "xabre0010@gmail.com",
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','purchase','stock','sale','account','project','event','sanbe_hr','purchase_request','hr_holidays','hr_attendance','calendar','hr_payroll_community','hr_contract','hr_gamification'],
    "data": [
        "data/hitung_employee_ws.xml",
        "data/sequence_employee_id.xml",
        "security/hr_branch_security.xml",
        "security/ir.model.access.csv",
        "views/department.views.xml",
        "views/directorate.views.xml",
        "views/division.views.xml",
        "views/emp_group_views.xml",
        "views/employee_level.xml",
        "views/hr_contracts.xml",
        "views/hr_employee.xml",
        "views/hr_menu_item_views.xml",
        "views/hr_profesion_views.xml",
        "views/job_status_views.xml",
        "views/hr_service_contract.xml",
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/banner.png"],
}