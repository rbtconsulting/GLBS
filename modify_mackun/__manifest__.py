# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2015-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Sreejith P(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Modify Mackun",
    'version': "",
    'author': 'jha',
    'company': '',
    'summary': 'modify mackun.',
    'website': '',
    'license': "",
    'category': "hris",
    'depends': [
        'base',
        'base_setup',
        'web',
        'web_kanban',
        'im_livechat',
        'report',
        'website',
        'mail',
        'resource',
        'backend_theme_v10',
        'employee_kra',
        'employee_stages',
        'employee_documents_expiry',
        'employee_check_list',
        'advance_salary',
        'hr',
        'hris',
        'hr_payroll',
        'hr_family',
        'hr_recruitment',
        'hr_expense',
        'hr_emergency_contact',
        'hr_holidays',
        'hr_public_holidays',
        'hr_employee_loan',
        'hr_attendance',
        'hr_contract',
        'hr_timesheet_attendance',
        'hr_experience',
        'hr_emergency_contact',
        'hr_payslip_monthly_report',
        'account',
        'survey',

    ],
    'data': [
        #"security/ir.model.access.csv",
        'views/modify_mackun.xml',
        'views/web_assets.xml',

        #"views/journal_entry.xml",
    ],
    'installable': True,
    'active': False,
    'auto_install': False,
}