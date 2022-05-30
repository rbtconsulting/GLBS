{
	'name': 'HR Payroll Reports',
	'description': 'HR Payroll Reports',
	'author': 'Rivista Solutions',
	'depends': [
		'base',
		'report',
		'hr_payroll'
	],
	'application': True,
	'data': [
		'views/hr_payroll_report.xml',
		'views/report_hr_payroll_registry_template.xml',
		'wizard/hr_payroll_registry_view.xml',
	],
	'images': [
	],
}