# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models,fields,tools
from odoo.modules.module import get_module_resource
import base64

FIRST_QUARTER_OF_MONTH = [1, 4, 7, 10]
SECOND_QUARTER_OF_MONTH = [2, 5, 8, 11]
THIRD_QUARTER_OF_MONTH = [3, 6, 9, 12]

def get_quarter(month):
    """Returns the quarter of a month."""
    if month in FIRST_QUARTER_OF_MONTH:
        return 1
    elif month in SECOND_QUARTER_OF_MONTH:
        return 2
    elif month in THIRD_QUARTER_OF_MONTH:
        return 3

class ReportHRSalaryEmployee2307(models.AbstractModel):
    _name = 'report.hris.report_hrsalaryemployee2307'

    def get_employee_salary_details(self, form):
        emp_ids = form.get('employee_ids', [])
        atc_id = form.get('atc_id', False)
        atc_id = atc_id and atc_id[0]
        start_date = form.get('start_date')
        end_date = form.get('end_date')
        start_date1 = fields.Date.from_string(start_date).strftime('%m %d %y')
        end_date1 = fields.Date.from_string(end_date).strftime('%m %d %y')
        salary_rule_ids = form.get('salary_rule_ids', [])
        employees = self.env['hr.employee'].browse(emp_ids)
        atc = self.env['alphanumeric.tax.code'].browse(atc_id)
        
        percent_tax_witheld = form.get('percent_tax_witheld', 0.0)
        
        def get_salary_details(emp_id):
            
            qry = """
                SELECT SUM(pl.total),p.date_release
                    FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                LEFT JOIN hr_employee AS emp ON emp.id = p.employee_id
                LEFT JOIN resource_resource AS r ON r.id = emp.resource_id
                WHERE p.state = 'done' AND p.employee_id = {}
                AND p.date_from >= '{}' AND p.date_from <= '{}' AND pl.salary_rule_id in %s
                AND p.credit_note = False
                GROUP BY pl.code,p.date_release
            """.format(emp_id, start_date, end_date)
            
            self.env.cr.execute(qry, (tuple(salary_rule_ids),))
            res = self.env.cr.fetchall()
            return res

        emp_sal_details = []
        for employee in employees:
            info = {}
            emp_fname = employee.firstname
            emp_mname = employee.middlename
            emp_lname = employee.lastname
            empr_addr = ",".join(filter(lambda r: r !='', [employee.address_id.street or '',
                                employee.address_id.street2 or '', 
                                employee.address_id.city or '',
                                employee.address_id.state_id.name or '', 
                                employee.address_id.country_id.name or '']))
            
            emp_addr = ",".join(filter(lambda r: r != '', [employee.street or '',
                                employee.street2 or '', 
                                employee.city2 or '',
                                employee.state_id.name or '', 
                                employee.country_id.name or '']))
             
            emp_id = employee.id
            tin_no = employee.identification_id
            empr_name = employee.company_id.name
            empr_tin = employee.company_id.vat
            
            info['EMP_FNAME'] = emp_fname
            info['EMP_MNAME'] = emp_mname or ''
            info['EMP_LNAME'] = emp_lname
            info['EMP_ADDR'] = emp_addr
            info['EMP_ZIP'] = employee.zip or ''
            info['START_DATE'] = start_date1
            info['END_DATE'] = end_date1
            info['TIN_NO'] = tin_no or ''
            info['TAX_RATE'] = percent_tax_witheld or 0
            info['EMPR_NAME'] = empr_name or ''
            info['EMPR_ZIP'] = employee.address_id.zip or ''
            info['EMPR_ADDR'] = empr_addr or ''
            info['EMPR_TIN'] = empr_tin or ''
            
            quarters = {}
            quarters[1] = 0
            quarters[2] = 0
            quarters[3] = 0
            for amount,date_release in get_salary_details(emp_id):
                release_quarter = get_quarter(fields.Date.from_string(date_release).month)
                amount_of_income_payment = amount
                
                if release_quarter in quarters:
                    amount = quarters.get(release_quarter, 0) + amount_of_income_payment
                    quarters[release_quarter] = amount
                else:
                    quarters[release_quarter] = amount_of_income_payment
            
            info['SUBJECT'] = atc.description
            info['CODE'] = atc.code
            info['INCOME_PAYMENTS'] = quarters
            
            tax_withheld = 0
            total = 0
            total_first = 0
            total_second = 0
            total_third = 0
            for q,amount in quarters.items():
                if q == 1:
                    total_first += amount
                if q == 2:
                    total_second += amount
                if q == 3:
                    total_third += amount
                
                total += amount    
                tax_withheld += amount * (percent_tax_witheld/100.0)
            
            info['TOTAL_FIRST'] = total_first
            info['TOTAL_SECOND'] = total_second
            info['TOTAL_THIRD'] = total_third
            
            info['TAX_WITHHELD'] = tax_withheld
            
            info['TOTAL'] = total
            
            emp_sal_details.append(info)

        return emp_sal_details
    
    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_employee_salary_details = self.get_employee_salary_details(data['form'])
        img_path = get_module_resource('hris', 'static/src/img', '2307-2.jpg')

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs, 
            'image_2307': open(img_path, 'rb').read().encode('base64'),
            'get_employee_salary_details': get_employee_salary_details
        }
        
        return self.env['report'].render('hris.report_hrsalaryemployee2307_template', docargs)
    
