# -*- coding: utf-8 -*-
{
    'name': "Sanbe HR Department Code",

    'summary': "v",

    'description': """
   v
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
    'depends': ['base', 'hr','base_territory'],
    'data': [
        'views/hr_department.xml',
    ],
    'assets': {
        'web.assets_frontend': [
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/banner.png"],
}

