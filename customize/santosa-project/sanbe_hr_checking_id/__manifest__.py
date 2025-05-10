# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
    'name': "Sanbe HR Checking ID",

    'summary': "Sanbe HR Checking ID",

    'description': """
   Sanbe HR Checking ID
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
    'depends': ['base', 'hr','sanbe_hr_extended'],
    'data': [
        'views/hr_checking_id.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            "/sanbe_hr_checking_id/static/src/js/hr_checking_id.js"
        ],
        'web.assets_qweb': [
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/banner.png"],
}