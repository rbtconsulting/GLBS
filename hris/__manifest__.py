# -*- coding: utf-8 -*-
{
    'name': 'Human Resource Information System',
    'version': '1.1',
    'category': 'Human Resource',
    'author': 'Rivista Solutions Inc.',
    'summary': "Recruitment, Payroll, Attendance, Leaves",
    'description': """
Customizations of Human Resource modules
===========================================

Key Features
---------------


*  Three level of Access Rights

*  Payroll Registry, Statutory and BIR Reports

*  Payroll Statutory Tables

*  Recruitment and Employee 201 File

*  Leaves Allocation and Conversion Automation

*  Manage Employee Other Income, Salary Movement

*  Timekeeping and Attedance Monitoring 

*  Manage Multiple Work Schedule

*  Request for Change of Attendance

    """,
    'website': 'https://www.rivista.biz',
    'images': [
        'images/hr_department.jpeg',
        'images/hr_employee.jpeg',
        'images/hr_job_position.jpeg',
        'static/src/img/default_image.png',
        'img/1601-C.jpg',
        'img/1601-E.jpg',
        'img/2307.jpg',
        'img/2316.jpg',
    ],
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
        'survey', 'website_hr_recruitment'
    ],
    'data': [
        'security/hr_security_rule.xml',
        'security/ir.model.access.csv',
        'data/statutory_data.xml',
        'data/hr_holidays_recurring_cron.xml',
        'data/hr_information_data.xml',
        'data/hr_salary_rule_categories_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/payroll_attendance_data.xml',
        'data/ir_actions_view.xml',
        # 'data/system_parameters.xml',
        'data/hr_employee_barcode.xml',
        'data/leaves_type.xml',
        'data/timelog_parser_data.xml',
        'data/alphalist_data_column.xml',
        'data/alphanumeric_tax_code.xml',
        'data/hr_annualization_structure.xml',
        'data/bir1601c_report_data.xml',
        'data/res_bank_data.xml',
        
        'views/hr_employee_views.xml',
        'views/hr_attendance_change.xml',
        'views/hr_payroll_contribution_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_applicant_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_employee_schedule_view.xml',
        'views/hr_payroll_attendance_view.xml',
        'views/hr_attendance_request_view.xml',
        'views/hr_payroll_period_view.xml',
        'views/create_user_account.xml',
        'views/hr_experience_ext.xml',
        'views/hr_employee_clearance_view.xml',
        'views/hr_disciplinary_action.xml',
        'views/hr_salary_rule_view.xml',
        'views/hr_timelogs_view.xml',
        'views/web_assets.xml',
        'views/hr_menu_custom.xml',
        'views/res_config_views.xml',
        'views/hr_label_views_custom.xml',
        'views/access_rights_approver.xml',
        'views/access_rights_firstlevel.xml',
        'views/access_rights_hr.xml',
        'views/hr_report_config.xml',
        'views/job_offer.xml',
        'views/hr_prorate_configuration.xml',
        'views/hr_clearance_views.xml',
        'views/hr_biometric_view.xml',
        'views/access_rights_firstlevel_new.xml',
        'views/hr_salary_grade.xml',
        'views/group_menu_hider.xml',
        'views/bir_1601c_report_config_view.xml',
        'views/hr_holiday_setting_views.xml',
        'views/hr_recruitment_inherit_template.xml',

        'report/certificate_of_employment_temp1.xml',
        'report/certificate_of_employment_temp2.xml',
        'report/custom_layout.xml',
        'report/hr_employee_bir_report.xml',
        'report/hr_statutory_report.xml',
        'report/report_job_offer.xml',
        'report/report_job_offer_template.xml',
        'report/report_hr_salary_employee_1601c_template.xml',
        'report/report_hr_salary_employee_1601e_template.xml',
        'report/report_hr_salary_employee_2307_template.xml',
        'report/report_hr_salary_employee_2316_template.xml',
        'report/report_payslip_templates.xml',
        'report/report_hr_phic_template.xml',
        'report/report_hr_hdmf_template.xml',
        'report/report_hr_sss_template.xml',
        'report/report_hr_tax_template.xml',
        'report/report_hr_payroll_registry_template.xml',
        'report/report_hr_alphalist_template.xml',
        'report/report_13th_month.xml',
        'report/hr_payslip_report.xml',
        'report/hr_payslip_report_template_two.xml',
        'report/hr_payslip_report_template_three.xml',
        'report/report_personal_action_notice.xml',
        'report/report_personal_action_notice_template.xml',
    
        'wizard/hr_salary_employee_1601c_view.xml',
        'wizard/hr_salary_employee_1601e_view.xml',
        'wizard/hr_salary_employee_2307_view.xml',
        'wizard/hr_salary_employee_2316_view.xml',
        #'wizard/hr_payslip_view.xml',
        'wizard/hr_contribution_view.xml',
        'wizard/hr_employee_hdmf_view.xml',
        'wizard/hr_employee_sss_view.xml',
        'wizard/hr_employee_tax_view.xml',
        'wizard/hr_employee_phic_view.xml',
        'wizard/hr_payroll_registry_view.xml',
        'wizard/employee_13th_month_report.xml',
        'wizard/wizard_bank_account_report.xml',
        'wizard/hr_alphalist_view.xml',
        'wizard/certificate_of_employment.xml',
        'wizard/personal_action_notice.xml',
        'wizard/hr_annualization_view.xml',
        'wizard/hr_attandence_report_wizard.xml',
    ],
    'qweb': ['static/src/xml/devmode.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
