# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models

class ReportHrSalaryEmployee2307(models.AbstractModel):
    _name = 'report.hris.report_hrsalaryemployee1601e'

    def get_employee_salary_details(self, form):
        emp_ids = form.get('employee_ids', [])
        start_date = form.get('start_date', '01-2017')
        #end_date = form.get('end_date', '01-2017')
        #from_to = [start_date, end_date]

        employees = self.env['hr.employee'].browse(emp_ids)

        dt = datetime.strptime(start_date, '%Y-%m-%d')
        year, mnth = dt.year, dt.month
        #quarter = form.get('quarter', 'first')
        percent_tax_witheld = form.get('percent_tax_witheld', 8.0)

        #def get_months_per_quarter(quarter):
        #    MONTHS_PER_QUARTER ={
        #        'first': ['01', '02', '03'],
        #        'second': ['04', '05', '06'],
        #        'third': ['07', '08', '09'],
        #        'fourth': ['10', '11', '12'],
        #    }
        #    return MONTHS_PER_QUARTER[quarter]

        def get_month_year(m, y):
            return ('0' + str(m) if len(str(m)) == 1 else str(m)) + '-' +str(y)

        def get_salary_details(emp_id, period_covered):
            #date_covered = get_month_year(mnth, year)
            qry = """
                SELECT pl.code, SUM(pl.total)
                    FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                LEFT JOIN hr_employee AS emp ON emp.id = p.employee_id
                LEFT JOIN resource_resource AS r ON r.id = emp.resource_id
                WHERE p.state = 'done' AND p.employee_id = {}
                AND to_char(p.date_release,'mm-yyyy') = '{}' AND pl.code in ('GROSS','Gross', 'gross')
                GROUP BY pl.code, pl.total
            """.format(emp_id, period_covered)

            self.env.cr.execute(qry)
            return  dict(self.env.cr.fetchall())

        emp_sal_details = []
        period_covered = get_month_year(mnth, year)
        for employee in employees:
            d = {}            
            emp_fname = employee.firstname
	    emp_lname = employee.lastname
	    emp_mname = employee.middlename
            emp_addr = employee.address_id.name
            emp_id = employee.id
	    tin_no = employee.identification_id
	    tel_no = employee.work_phone
            """
                splucena
                Add additional employee details here
                Add additional employee details to dictionary
            """
            d.update({
                'EMP_FNAME': emp_fname,
		'EMP_MNAME': emp_mname,
		'EMP_LNAME' : emp_lname,
                'EMP_ADDR': emp_addr,
		'TEL_NO': tel_no,
		'TIN_NO': tin_no or '',
                'PERIOD_COVERED': period_covered.split('-'),
                'TAX_RATE': int(percent_tax_witheld)
            })
            emp_salary = get_salary_details(emp_id, period_covered)

            if emp_salary:
                amount_of_income_payment = float(emp_salary['GROSS']) * (float(percent_tax_witheld)/100.00)
                d.update({
                    'GROSS': emp_salary['GROSS'],
                    'TOTAL': amount_of_income_payment
                })
            emp_sal_details.append(d)

        return emp_sal_details

    def test(self, form):
        emp_ids = form.get('employee_ids', [])
        employees = self.env['hr.employee'].browse(emp_ids)

        emp = []
        for employee in employees:
            d ={}
            d.update({
                'emp_name': employee.name
                })
            emp.append(d)

        return emp

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_employee_salary_details = self.get_employee_salary_details(data['form'])

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_employee_salary_details': get_employee_salary_details
        }
        return self.env['report'].render('hris.report_hrsalaryemployee1601e_template', docargs)
    
