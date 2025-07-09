# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
##################################################################################
{
    'name': "Sanbe Employement Tracking",
    'summary': """
        Sanbe Employement Tracking
    """,
    'description': """
         Sanbe Employement Tracking
    """,
    'author': "Albertus Restiyanto Pramayudha",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','hr','base_territory','sanbe_hr_extended'],
    'data': [
        'views/hr_employment_tracking.xml',
        'views/hr_employment_log.xml',
        'views/hr_employee.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            "/sanbe_employment_tracking/static/src/js/employment_tracking.js"
        ],
        'web.assets_qweb': [
        ],
    },
}