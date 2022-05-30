# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models

class ReportHRTax(models.AbstractModel):
    _name = 'report.hris.report_tax_contribution_template'

    def get_tax_contribution_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_payroll = form.get('date_payroll', None)
        date_from = form.get('date_from', None)
        date_to = form.get('date_to', None)

        employees = self.env['hr.employee'].browse(emp_ids)

        def get_tax_contribution(emp_id, date_from, date_to):
            query = """
                SELECT pl.code, SUM(pl.total)
                FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                WHERE p.date_release >= '{}' AND p.date_release <= '{}'
                AND p.state = 'done' AND p.credit_note = False AND p.employee_id = {}
                GROUP BY pl.code
            """.format(date_from, date_to, emp_id)

            self.env.cr.execute(query)

            results = self.env.cr.fetchall()
            if results:
                return [dict(results)]
            return []

        emp_tax_contribution = []
   
        TOTAL_ROWS = 0
        TOTAL_TAX = 0.0
        TOTAL_TAX_CON = 0.0

        for employee in employees:
            details = {}
            emp_name = employee.name
            emp_addr = employee.address_id.name
            emp_barcode = employee.barcode
            emp_id = employee.id
            emp_tin = employee.identification_id
            emp_position = employee.job_id.name

            details['EMP_NAME'] = emp_name or ''
            details['EMP_ADDR'] = emp_addr or ''
            details['EMP_POS'] = emp_position or ''
            details['EMP_NUM'] = emp_barcode or ''
            details['EMP_TIN'] = emp_tin or ''
            
            details['WTHTAX'] = 0
            
            results = get_tax_contribution(emp_id, date_from, date_to)
            if results:
                SUBTOTAL_TAX = 0
                
                for values in results:
                    SUBTOTAL_TAX += values.get('WTHTAX-SM', 0) + values.get('WTHTAX-M', 0)
                
                details['WTHTAX'] = SUBTOTAL_TAX
                TOTAL_TAX_CON += SUBTOTAL_TAX
                
            emp_tax_contribution.append(details)
            TOTAL_ROWS += 1

        emp_tax_contribution.append({
            'TOTAL_ROWS': TOTAL_ROWS,
            'TOTAL_TAX': TOTAL_TAX,
            'TOTAL_TAX_CON': TOTAL_TAX_CON
        })

        return emp_tax_contribution

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_tax_contribution_details = self.get_tax_contribution_details(data['form'])
        date_payroll = datetime.strptime(data['form'].get('date_payroll'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_to = datetime.strptime(data['form'].get('date_to'), '%Y-%m-%d').strftime('%B %d, %Y')


        details = get_tax_contribution_details[:-1]
        totals = get_tax_contribution_details[-1]

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
            'get_tax_contribution_details': details,
            'totals': totals,
            'dates': dates,
        }
        
        return self.env['report'].render('hris.report_tax_contribution_template', docargs)




