# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models

class ReportPHIC(models.AbstractModel):
    _name = 'report.hris.report_phic'
    
    #get philhealth contributions and employee details 
    def get_phic_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_from = form.get('date_from', None)
        date_to = form.get('date_to', None)
        
        def format_date(str_date):
            date_format = datetime.strptime(str_date, '%Y-%m-%d').strftime('%Y-%m-%d')            
            return date_format

        def get_phic_registry(emp_id, date_from, date_to):
            query = """
                SELECT pl.code, SUM(pl.total)
                FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                WHERE p.date_from >= '{}' AND p.date_from <= '{}'
                AND p.state = 'done' AND p.credit_note = False AND p.employee_id = {}
                GROUP BY pl.code
                
            """.format(date_from, date_to, emp_id)

            self.env.cr.execute(query)
            res = self.env.cr.fetchall()

            if res:
                return [dict(res)]
            return []

        emp_phic_registry = []
        
        TOTAL_PHIC_EE = 0.0
        TOTAL_PHIC_ER = 0.0
        TOTAL_PHIC = 0.0
        
        #get employee details
        employees = self.env['hr.employee'].browse(emp_ids)
        
        for employee in employees:
            details = {}            
            emp_first = employee.firstname
            emp_middle = employee.middlename
            emp_surname = employee.lastname
            emp_phic = employee.phic_no
            emp_id = employee.id
            
            details['EMP_FIRST'] = emp_first
            details['EMP_MIDDLE'] = emp_middle
            details['EMP_SURNAME'] = emp_surname
            details['EMP_PHIC'] = emp_phic
            details['EMP_NUM'] = emp_id
            
            details['PHIC_EE'] = 0
            details['PHIC_ER'] = 0
            
            results = get_phic_registry(emp_id, date_from, date_to)
            if results:                
                SUBTOTAL_PHIC_EE = 0
                SUBTOTAL_PHIC_ER = 0
                SUBTOTAL_PHIC = 0
                
                for values in results:
                    
                    SUBTOTAL_PHIC_EE += values.get('PHIC-M', 0.0 ) + values.get('PHIC-SM', 0.0) 
                    SUBTOTAL_PHIC_ER += values.get('PHICER-SM', 0.0) + values.get('PHICER-M', 0.0)
                    SUBTOTAL_PHIC +=  SUBTOTAL_PHIC_EE + SUBTOTAL_PHIC_ER
                
                details['PHIC_EE'] = SUBTOTAL_PHIC_EE
                details['PHIC_ER'] = SUBTOTAL_PHIC_ER
            
                TOTAL_PHIC_EE += SUBTOTAL_PHIC_EE 
                TOTAL_PHIC_ER += SUBTOTAL_PHIC_ER
                TOTAL_PHIC +=  SUBTOTAL_PHIC
                
            emp_phic_registry.append(details)
    
        emp_phic_registry.append({
            'TOTAL_PHIC_EE' : TOTAL_PHIC_EE,
            'TOTAL_PHIC_ER': TOTAL_PHIC_ER,
            'TOTAL_PHIC' : TOTAL_PHIC
        })

        return emp_phic_registry

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_phic_details = self.get_phic_details(data['form'])
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_to = datetime.strptime(data['form'].get('date_to'), '%Y-%m-%d').strftime('%B %d, %Y')
        
        details = get_phic_details[:-1]
        totals = get_phic_details[-1]

        dates = {
            
            'DATE_FROM': date_from,
            'DATE_TO': date_to,            
        }
   
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_phic_details': details,
            'totals': totals,
            'dates': dates,
        }
        return self.env['report'].render('hris.report_phic_template', docargs)
    
