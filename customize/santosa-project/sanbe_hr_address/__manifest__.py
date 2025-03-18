# -*- coding: utf-8 -*-
#################################################################################
# Author    => Rohim Muhamad
# email     => rohimuhamadd@gmail.com
#################################################################################
{
    'name': "Sanbe HR Employee Addresses",

    'summary': """
        customization for employee to be able to have multiple address
    """,

    'description': """
        1. Change page name work information -> address information
        2. Change page name private information -> job information
        3. Custom add employee list address inside tab work information
    """,

    'author': "Rohim Muhamad",
    'website': "http://www.yourcompany.com",
    "support": "rohimuhamadd@gmail.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        # 'views/hr_employee_address.xml',
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
