# -*- coding:utf-8 -*-

from datetime import datetime

from odoo import api, models

class ReportAlphalist(models.AbstractModel):
    _name = 'report.hris.report_alphalist_template'

    def get_alphalist_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_from = form.get('date_from', None)
        date_to = form.get('date_to', None)

        employees = self.env['hr.employee'].browse(emp_ids)

        dt_from = datetime.strptime(date_from, '%Y-%m-%d')
        dt_to = datetime.strptime(date_to, '%Y-%m-%d')

        def format_date(str_date):
            dt = datetime.strptime(str_date, '%Y-%m-%d')
            year, mnth, day = dt.year, dt.month, dt.day

            day = '0' + str(day) if len(str(day)) == 1 else day
            mnth = '0' + str(mnth) if len(str(mnth)) == 1 else mnth
            return '-'.join([str(mnth), str(day), str(year)])

        def get_alphalist_contribution(emp_id, date_from, date_to):
            qry = """
                SELECT pl.code, SUM(pl.total)
                FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                WHERE to_char(p.date_release, 'mm-dd-yyyy') >= '{}' AND to_char(p.date_release, 'mm-dd-yyyy') <= '{}'
                AND p.state = 'done' AND p.credit_note = False AND p.employee_id = {}
                GROUP BY pl.code, he.name_related, pl.total
                ORDER BY he.name_related
            """.format(date_from, date_to, emp_id)

            self.env.cr.execute(qry)
            d = self.env.cr.fetchall()
            if d:
                return [dict(d)]
            return []

        emp_alphalist = []
        totals =[]
        SEQ_NO = 1
        TOTAL_ROWS = 0
        TOTAL_GROSS = 0.0
        TOTAL_SSS_HDMF_PHIC = 0.0
        TOTAL_BASIC = 0.0

        for employee in employees:
            d = {}
            emp_fname = employee.firstname
            emp_mname = employee.middlename
            emp_lname = employee.lastname
            emp_addr = employee.address_id.name
            emp_id = employee.id
            emp_position = employee.job_id.name
            emp_tin = employee.identification_id


            d.update({
                'EMP_FNAME': emp_fname,
                'EMP_MNAME': emp_mname,
                'EMP_LNAME':emp_lname,
                'EMP_ADDR': emp_addr or '',
                'EMP_POS': emp_position or '',
                'EMP_NUM': emp_id,
                'EMP_TIN': emp_tin


            })

            hr_salary_rule = self.env['hr.salary.rule'].search([])
            hr_salary_code = dict((code, 0) for code in hr_salary_rule.mapped('code'))
            d.update(hr_salary_code)

            alpha = get_alphalist_contribution(emp_id, format_date(date_from), format_date(date_to))
            if alpha:
                LEN_LS_ITEMS = len(alpha)
                for al in alpha:
                    TOTAL_GROSS += al.get('GROSS', 0.00)
                    TOTAL_SSS_HDMF_PHIC += al.get('SSS-SM', 0.00) + al.get('SSS-M', 0.00) + al.get('HDMF-SM', 0.00) + al.get('HDMF-M', 0.00) + al.get('PHIC-SM', 0.00) + al.get('PHIC-M', 0.00)
                    TOTAL_BASIC += al.get('BASIC',0.00)
                    d.update(al)

            emp_alphalist.append(d)
            TOTAL_ROWS += 1



        emp_alphalist.append({
            'SEQ_NO' : SEQ_NO,
            'TOTAL_ROWS': TOTAL_ROWS,
            'TOTAL_GROSS': TOTAL_GROSS,
            'TOTAL_SSS_HDMF_PHIC': TOTAL_SSS_HDMF_PHIC,
            'TOTAL_BASIC': TOTAL_BASIC,



        })

        return emp_alphalist

    def get_company(self, form):
        company_id = form.get('company_id', False)[1]
        company = {
           'company_id': company_id

        }

        return company

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_alphalist_details = self.get_alphalist_details(data['form'])
        date_payroll = datetime.strptime(data['form'].get('date_payroll'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_to = datetime.strptime(data['form'].get('date_to'), '%Y-%m-%d').strftime('%B %d, %Y')
        company_id = self.get_company(data['form'])

        details = []
        totals = []

        total_record = len(get_alphalist_details) - 1
        for index, record in enumerate(get_alphalist_details):
            if index != total_record:
                details.append(record)
            else:
                totals.append(record)

        dates = {
            'DATE_PAYROLL': date_payroll,
            'DATE_FROM': date_from,
            'DATE_TO': date_to,

        }

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_alphalist_details': details,
            'totals': totals,
            'dates': dates,
            'company_id': company_id
        }
        return self.env['report'].render('hris.report_alphalist_template', docargs)




