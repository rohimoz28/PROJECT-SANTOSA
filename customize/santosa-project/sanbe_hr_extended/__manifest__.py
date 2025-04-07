# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

{
    'name': "Sanbe HR Extended",

    'summary': "Sanbe HR Extended",

    'description': """
   Sanbe HR Extended
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
    'depends': ['base', 'hr','sanbe_hr','hr_payroll_community','hr_contract'],
    "data": [
        "data/hitung_employee_ws.xml",
        "data/sequence_employee_id.xml",
        "security/hr_branch_security.xml",
        "security/ir.model.access.csv",
        "views/emp_group_views.xml",
        "views/employee_level.xml",
        "views/hr_contracts.xml",
        "views/department.views.xml",
        "views/directorate.views.xml",
        "views/division.views.xml",
        "views/hr_employee.xml",
        "views/hr_profesion_views.xml"
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

