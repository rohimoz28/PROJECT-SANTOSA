# -*- coding: utf-8 -*-
{
	'name': "Sanbe HR Certification",
	'summary': """Sanbe HR Certification""",
	'description': """Sanbe HR Certification""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Human Resources',
	'version': '17.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'hr'],
	'price': 25.00,
	'currency': 'EUR',
	'support': 'xabre0010@gmail.com',
	'data': [
		'data/generate_certivicate_checker_cron.xml',
		'security/ir.model.access.csv',
		'views/certificated_type.xml',
		'views/hr_employee_certification.xml',
		'views/hr_employee.xml',
	],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'assets': {
		'web.assets_backend': [
		],
		'web.assets_qweb': [
		],
	},
	'installable': True,
	'application': True,
	'auto_install': False,
}
