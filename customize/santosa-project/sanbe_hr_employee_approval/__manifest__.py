# -*- coding: utf-8 -*-
{
	'name': "Sanbe HR Employee Approval",
	'summary': """Sanbe HR Employee Approval""",
	'description': """Sanbe HR Employee Approval""",
	'author': "Albertus Restiyanto Pramayudha",
	'website': 'https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/',
	'category': 'Human Resources',
	'version': '17.1.1',
	'license': 'OPL-1',
	'depends': [
     	'base', 
      	'hr',
       	'hr_skills',
        'sanbe_hr_extended',
        'sanbe_employement_details',
        'base_territory',
        'sanbe_employment_tracking'],
	'price': 25.00,
	'currency': 'EUR',
	'support': 'xabre0010@gmail.com',
	'data': [
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
