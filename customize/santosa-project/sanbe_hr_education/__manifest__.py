# -*- coding: utf-8 -*-
{
	'name': "Sanbe HR Educations",
	'summary': """Sanbe HR Educations""",
	'description': """Sanbe HR Educations""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Human Resources',
	'version': '17.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'sanbe_hr_certification'],
	'support': 'xabre0010@gmail.com',
	'data': [
		'security/ir.model.access.csv',
		'views/hr_education_details.xml',
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
