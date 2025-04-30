# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
    'name': "Sanbe Employement Details",
    'summary': """
        Sanbe Employement Details
    """,
    'description': """
         Sanbe Employement Details
    """,
    'author': "Albertus Restiyanto Pramayudha",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','hr','sanbe_hr_extended'],
    'data': [
        'views/hr_employement_details.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}