# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
{
    'name': "Sanbe HR Payroll",
    'summary': "Sanbe HR Payroll",
    'description': """
            Sanbe HR Payroll
    """,
    'author': "Albertus Restiyanto Pramayudha",
    'website': "http://www.yourcompany.com",
    "support": "xabre0010@gmail.com",
    'category': 'Human Resource',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sanbe_hr_tms','hr_payroll_community', 'sanbe_hr_extended'],
    'data': [
        'views/hr_payroll_entry.xml',
        'views/sb_bank_transfer_summary.xml',
        'views/sb_monthly_tax_summary.xml',
        # 'views/sb_monthly_tax_summary_detail.xml',
        'views/sb_payroll_summary.xml',
        'views/sb_insurance_setting.xml',
        'views/sb_payroll_entry.xml',
        'views/sb_payroll_entry_detail.xml',
        'views/sb_employee_profile.xml',
        'views/sb_compensation.xml',
        'views/sb_tax_setting.xml',
        'views/sb_payroll_employee.xml',
        'views/sb_allowance_deduction.xml',
        'views/sb_allowance_deduction.xml',
        'views/sb_tax_yearly.xml',
        'views/sb_ptkp_setting.xml',
        'views/hr_payroll_menu.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
            'web.assets_backend': [
                'hr_holidays/static/src/**/*',
            ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/banner.png"],
}