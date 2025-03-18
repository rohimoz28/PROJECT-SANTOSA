# -*- coding: utf-8 -*-
###############################################################################

###############################################################################
{
    'name': 'Sanbe One2many Standard',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Quick Search Feature For One2many Fields In Odoo',
    'description': """This module enables users to search for text within
    One2many fields. The rows that match the search criteria will be displayed,
    while others will be hidden.""",
    'author': "Albertus Restiyanto Pramayudha",
    'website': "http://www.yourcompany.com",
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'sanbe_one2many_standard/static/src/css/header.css',
            'sanbe_one2many_standard/static/src/css/widget.css',
            'sanbe_one2many_standard/static/src/scss/stycki_header.scss',
            'sanbe_one2many_standard/static/src/js/sanbe_exportdata_dialog.js',
            'sanbe_one2many_standard/static/src/js/sanbe_one2many.js',
            'sanbe_one2many_standard/static/src/xml/sanbe_one2many.xml',
            'sanbe_one2many_standard/static/src/scss/form_sheet_fullscreen.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    "application": False,
}
