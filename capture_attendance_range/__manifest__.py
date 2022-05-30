# -*- coding: utf-8 -*-
{
    'name': "capture_attendance_range",

    'summary': """""",

    'description': """

    """,

    'author': "MBM",
    'website': "http://www.yourcompany.com",


    'category': 'Uncategorized',
    'version': '0.1',


    'depends': ['base', 'hris'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/capture_attendance_cron.xml',
        'wizard/capture_attendance.xml',
    ],

}