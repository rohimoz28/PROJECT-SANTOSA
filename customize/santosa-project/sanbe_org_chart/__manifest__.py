# -*- coding: utf-8 -*-
{
	'name': "Sanbe Organization Chart",
	'summary': """Employee Hierarchy - Multi Company - Drag and Drop - Search - Add - Edit - Delete - Screenshot - Horizontal - Vertical""",
	'description': """Dynamic Display of your Employee Hierarchy""",
	'author': "Albertus Restiyanto Pramayudha",
	"website": "https://slifeorganization.com",
	'category': 'Human Resources',
	'version': '17.1.1',
	'license': 'OPL-1',
	'depends': ['base', 'hr','hr_org_chart','base_territory'],
	'price': 25.00,
	'currency': 'EUR',
	'support': 'frejusarnaud@gmail.com',
	'data': [
		'data/slife_org_chart_data.xml',
		'security/ir.model.access.csv',
		'views/org_chart_views.xml',
		'views/hr_department.xml',
		'views/disable_odoo_chart.xml',
	],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'assets': {
		'web.assets_backend': [
			"/sanbe_org_chart/static/src/js/org_chart_employee.js",
			"/sanbe_org_chart/static/src/js/jquery_orgchart.js",
			"/sanbe_org_chart/static/src/js/other.js",
			"/sanbe_org_chart/static/src/js/jspdf_min.js",
			"/sanbe_org_chart/static/src/js/html2canvas_min.js",
			"/sanbe_org_chart/static/src/css/jquery_orgchart.css",
			"/sanbe_org_chart/static/src/css/style.css",
			"/sanbe_org_chart/static/src/xml/org_chart_employee.xml",
		],
		'web.assets_qweb': [
		],
	},
	'installable': True,
	'application': True,
	'auto_install': False,
}
