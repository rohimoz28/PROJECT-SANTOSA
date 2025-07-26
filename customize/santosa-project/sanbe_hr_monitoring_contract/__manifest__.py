# -*- coding: utf-8 -*-
{
    'name': "Sanbe HR Monitoring Contract",

    'summary': "Sanbe HR Monitoring Contract",

    'description': """
   Sanbe HR Monitoring Contract
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
    'depends': ['base', 'hr','hr_skills','hr_resignation','hr_skills_survey','hr_presence','base_territory','sanbe_employement_details'],
    "data": [
        "security/contract_monitoring_rule.xml",
        "security/ir.model.access.csv",
        "data/generate_contract_reminder_cron.xml",
        "data/mail_template.xml",
        "wizards/hr_monitoring_contract.xml",
        "views/employee_monitoring.xml",
        "views/hr_employee_contract_monitoring_views.xml",
        "views/hr_mail_config_views.xml"
    ],
    'assets': {
        'web.assets_backend': [
            "/sanbe_hr_monitoring_contract/static/src/js/hr_monitoring_controller.js",
            "sanbe_hr_monitoring_contract/static/src/css/tree_table.css",
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

