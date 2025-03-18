# -*- coding: utf-8 -*-
{
    'name': "Sanbe HR Dashboard",

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
    'depends': ['base', 'sale', 'sanbe_hr_resignation', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/dashboard_security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/dashboard_views.xml',
        'views/dashboard_menu_views.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Load Chart.js first if needed
            ('include', 'web/static/lib/Chart/Chart.js'),
            #('include', '/web/static/lib/chartjs-plugin-annotation/chartjs-plugin-annotation.min.js'),
            # Then load your module's files
            '/sanbe_hr_dashboard/static/src/js/chart_renderer.js',
            '/sanbe_hr_dashboard/static/src/js/sanbe_dashboard.js',
            '/sanbe_hr_dashboard/static/src/xml/sanbe_dashboard.xml',
            # '/sanbe_hr_dashboard/static/src/js/sanbe_dashboard2.js',
            # '/sanbe_hr_dashboard/static/src/xml/sanbe_dashboard2.xml',
        ],
    },

    'installable': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

