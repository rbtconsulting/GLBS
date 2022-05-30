# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to odoo
#
#    Copyright (C) 2016 - Turkesh Patel. <http://www.almightycs.com>
#
#    @author Turkesh Patel <info@almightycs.com>
###########################################################################

{
    'name': 'Employee Performance Evaluation by KRA/Value Rating',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Employee Performance Evaluation by KRA(Key Result Area)/KPA(Key Performance Area)',
    'description':"""Emplyee performance evaluation by KRA(Key Result Area)/KPA(Key Performance Area)
    HR Evaluation
    Employee Evaluation
    Emplyee Performance Calculation
    Employee Appraisals""",
    'author': 'Almighty Consulting Services',
    'depends': ['hr'],
    'website': 'http://www.almightycs.com',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/kra_view.xml',
        'views/value_rating_view.xml',
        'report/kra_report.xml',
        'report/value_rating_report.xml',
        'wizard/create_kra_view.xml',
        'data/data.xml', 
    ],
    'images': [
        'static/description/hr_evaluation_kra_odoo_cover.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 31,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
