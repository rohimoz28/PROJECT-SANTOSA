# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

{
    'name': "Sanbe HR PAM",

    'summary': "Sanbe HR PAM",

    'description': """
   Sanbe HR PAM
    """,

    'author': "Sanbe IT Corp",
    'website': "http://www.yourcompany.com",
    "support": "info@sanbe-farma.com",
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','sanbe_hr','hr_payroll_community','hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_emp_status.xml',
        'views/hr_employee.xml'
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

