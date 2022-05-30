{
	'name': 'Employee Reports',
	'description': 'Extend hr_module to include reports.',
	'author': 'Rivista Solutions',
	'depends': [
		'base',
		'report',
	],
	'application': True,
	'data': [
		'reports/report_employee_master_list.xml',
		'reports/report_employee_201.xml'
	],
	'images': [
	],
}