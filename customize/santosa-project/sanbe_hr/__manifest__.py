# -*- coding: utf-8 -*-
{
    'name': "Sanbe HR",

    'summary': "Sanbe HR",

    'description': """
    This module offers users the ability to personalize their login experience by uploading background images or selecting background color schemes. This feature enhances visual appeal, fosters brand consistency, and creates a user-friendly authentication environment. Users can preview 
    real-time changes and align the login page with their aesthetic preferences or organizational branding.
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
    'depends': ['base', 'ohrms_core', 'hr','base_territory'],
    'data': [

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

