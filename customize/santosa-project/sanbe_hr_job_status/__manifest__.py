# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
    'name': "Sanbe HR Job Status",

    'summary': "Sanbe HR Job Status",

    'description': """
   Sanbe HR Job Status
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
    'depends': ['base', 'hr'],
    'data': [
        'views/hr_job_status.xml',
        'security/ir.model.access.csv',
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