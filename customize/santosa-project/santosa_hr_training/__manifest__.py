# -*- coding: utf-8 -*-
{
    'name': "santosa_hr_training",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','sanbe_hr_extended','sanbe_hr_certification'],

    # always loaded
    "data": [
        "views/hr_training_views.xml",
        "views/templates.xml",
        "views/views.xml",
        "security/ir.model.access.csv"
    ],
    
    'assets': {
        'web.assets_backend': [
            'santosa_hr_training/static/src/css/feature1.css',
        ]
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

