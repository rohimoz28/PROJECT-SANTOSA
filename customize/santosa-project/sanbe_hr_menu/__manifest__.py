# -*- coding : utf-8 -*-
{
    'name': "Sanbe HR Menus",
    'summary': "Sanbe HR Menus",
    'description': """
                Sanbe HR Menus
            """,

    'author': "Albertus Restiyanto Pramayudha, Azizah Nurmahdyah",
    'website': "https://sanbe-farma.com/",
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',
    'depends': ['base', 'hr','hr_contract','hr_recruitment','hr_gamification','hr_skills'],
    'data': [
        'views/hr_menus.xml',
    ],
    'assets': {
        'web.assets_frontend': [],
    },
    "images": ["static/description/banner.png"],
}