# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models

class Report13thMonth(models.AbstractModel):
    _name = 'report.hris.report_13thmonth_template'

    def get_13thmonth_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_from = form.get('date_from', None)
        date_to = form.get('date_to', None)

        employees = self.env['hr.employee'].browse(emp_ids)

        def format_date(str_date):
            date_format = datetime.strptime(str_date, '%Y-%m-%d').strftime('%m-%d-%Y')
            return date_format

        def get_payslip_lines(emp_id, date_from, date_to):
            payslip_lines = """SELECT payslip.salary_rule_id, sum(payslip.total) as total
                                FROM ((SELECT pl.salary_rule_id as salary_rule_id, sum(pl.total) as total
                                        FROM hr_payslip_line AS pl
                                        LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                                        LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id)
                                        LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                                        WHERE p.date_release >= '{}' AND p.date_release <= '{}'
                                        AND p.employee_id = {} AND p.state = 'done' AND p.credit_note = False
                                        GROUP BY pl.salary_rule_id,he.name_related ORDER BY he.name_related)
                                        
                                        UNION (SELECT pl.salary_rule_id as salary_rule_id, -sum(pl.total) as total
                                            FROM hr_payslip_line AS pl
                                            LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                                            LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id)
                                            LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                                            WHERE p.date_release >= '{}' AND p.date_release <= '{}'
                                            AND p.credit_note = True AND p.employee_id = {} AND p.state = 'done' AND p.credit_note = False
                                            GROUP BY pl.salary_rule_id, he.name_related ORDER BY he.name_related)) payslip GROUP BY  payslip.salary_rule_id
                        """.format(date_from, date_to, emp_id, date_from, date_to, emp_id)
            self.env.cr.execute(payslip_lines)
            res = self.env.cr.fetchall()
            if res:
                return [dict(res)]
            return []

        emp_13thmonth = []

        TOTAL_emp13thmonth = 0
        for employee in employees:
            
            results = {}
            BASIC = 0
            DEDUCTION = 0
            emp13thmonth = 0
            
            results['EMPLOYEE'] = employee
            res_payslip_lines = get_payslip_lines(employee.id, format_date(date_from), format_date(date_to))
            results['DEDUCTION'] = DEDUCTION
            results['BASIC'] = BASIC
            results['emp13thmonth'] = emp13thmonth
            
            if res_payslip_lines:
                template_conf = self.env['hr.th.month_pay.config'].search([])
                addition = template_conf.config_line.filtered(lambda r:r.condition == 'add')
                subtract = template_conf.config_line.filtered(lambda r:r.condition == 'subtract')
                
                #Year to Date inclusion on 13th Month Pay
                add_ids = addition.ytd_config_ids.ids
                subtract_ids = subtract.ytd_config_ids.ids
                
                if add_ids or subtract_ids:
                    BASIC += sum([self.env['hr.year_to_date.line'].\
                                                   get_previous_ytd(employee.id, 
                                                   add_ids, 
                                                   date_from, date_to).get(r, 0) \
                                                   for r in add_ids])
                    
                    DEDUCTION += sum([self.env['hr.year_to_date.line'].\
                                                   get_previous_ytd(employee.id, 
                                                   subtract_ids, 
                                                   date_from, date_to).get(r, 0) \
                                                   for r in subtract_ids])
                    
                for rpl in res_payslip_lines:  
                    #Salary Rules
                    add_codes = addition.salary_rule_ids.mapped('id')
                    subtract_codes = subtract.salary_rule_ids.mapped('id')
                    BASIC += sum([rpl.get(code, 0) for code in add_codes])
                    DEDUCTION += sum([rpl.get(code, 0) for code in subtract_codes])
                    emp13thmonth += (BASIC - DEDUCTION) / 12.0
                    
                results['emp13thmonth'] = emp13thmonth
                TOTAL_emp13thmonth += emp13thmonth
            emp_13thmonth.append(results)
        emp_13thmonth.append({'TOTAL_emp13thmonth': TOTAL_emp13thmonth})

        return emp_13thmonth

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_13thmonth_details = self.get_13thmonth_details(data['form'])
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_to = datetime.strptime(data['form'].get('date_to'), '%Y-%m-%d').strftime('%B %d, %Y')
        
        details = get_13thmonth_details[:-1]
        totals = get_13thmonth_details[-1]
 
        dates = {'date_from': date_from,
                 'date_to': date_to}

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'totals': totals,
            'get_13thmonth_details': details,
            'dates': dates,
        }

        return self.env['report'].render('hris.report_13thmonth_template', docargs)
