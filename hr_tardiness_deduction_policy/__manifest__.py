# -*- coding: utf-8 -*-
{
    'name': 'HRIS Tardiness',
    'version': '1.1',
    'category': 'Human Resource',
    'author': 'Rivista Solutions Inc.',
    'summary': "Recruitment, Payroll, Attendance, Leaves",
    'description': """

    """,
    'website': 'MBM',
    'images': [],
    'depends': ['base', 'hris', 'hr_payroll'

                ],
    'data': [
        'data/salary_rules.xml',
        'views/tardiness_table_views.xml'],
    'qweb': [''],
    'installable': True,
    'application': True,
    'auto_install': False,
}
