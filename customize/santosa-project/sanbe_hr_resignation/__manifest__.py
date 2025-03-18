# -*- coding : utf-8 -*-

{
    'name': "Sanbe HR Resignation",

    'summary': "Sanbe HR Resignation",

    'description': """
  Sanbe HR Resignation
    """,

    'author': "PT. Sanbe Farma",
    'website': "http://www.yourcompany.com",
    "support": "xabre0010@gmail.com",
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_resignation','base_territory','sanbe_hr_extended','sanbe_hr_employee_approval'],
    'data': [
        'security/hr_resignation_security.xml',
        'views/hr_resignation.xml',
        # 'reports/rpt_paklaring.xml',
        'reports/paklaring_report.xml',
        'reports/paklaring_report_steril.xml',
        'reports/FKPD_report.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        "web.assets_backend": [
            "sanbe_hr_resignation/static/src/js/hr_resignation_search.js",
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/banner.png"],
}