# -*- coding: utf-8 -*-
{
	'name': "Sanbe HR Employee Mutation",
	'summary': """Sanbe HR Employee Mutation""",
	'description': """Sanbe HR Employee Mutation""",
	'author': "Albertus Restiyanto Pramayudha, Azizah Nurmahdyah",
	'website': 'https://sanbe-farma.com/',
	'category': 'Human Resources',
	'version': '17.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'hr','sanbe_hr_extended','base_territory','sanbe_hr_service_type','sanbe_hr_employee_approval'],
	'price': 25.00,
	'currency': 'EUR',
	'data': [
        # security
        'security/mutation_groups.xml',
		'security/ir.model.access.csv',
		'security/ir.security.rules.xml',
        # view
		'views/hr_employee_mutation.xml',
        # data
		'data/cron_hr_check_mutation.xml',
		'data/mutation_seq_number.xml',
        # store procedure
        'db/update_intermediate.sql',
        # report
        'reports/FKPM_report.xml',
	],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'assets': {
		'web.assets_backend': [
			"/sanbe_hr_employee_mutation/static/src/js/mutation_form.js"
		],
		'web.assets_qweb': [
		],
	},
	'installable': True,
	'application': True,
	'auto_install': False,
}
