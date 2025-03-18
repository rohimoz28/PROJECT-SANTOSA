# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
    'name': "Sanbe HR Warning Letter",

    'summary': "Sanbe HR Warning Letter",

    'description': """
 Sanbe HR Warning Letter
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
        'views/hr_pasal_pelanggaran.xml',
        'views/hr_warning_letter_type.xml',
        'views/hr_warning_letter.xml',
        'data/hr_warning_letter_seq.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            "/sanbe_hr_warning_letter/static/src/js/hr_warning_letter.js"
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