# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models

class ReportHRHMDF(models.AbstractModel):
    _name = 'report.hris.report_hdmf_contribution_template'

    def get_hdmf_contribution_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_payroll = form.get('date_payroll', None)
        date_from = form.get('date_from', None)
        date_to = form.get('date_to', None)

        employees = self.env['hr.employee'].browse(emp_ids)

        def get_hdmf_contribution(emp_id, date_from, date_to):
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

        emp_hdmf_contribution = []
        TOTAL_ROWS = 0
        TOTAL_HDMFER = 0.0
        TOTAL_HDMF = 0.0
        TOTAL_HDMF_CON = 0.0
        MONTHLY_COMPENSATION = 0.0

        for employee in employees:
            details = {}
            emp_name = employee.name
            emp_first = employee.firstname
            emp_middle = employee.middlename
            emp_surname = employee.lastname
            emp_addr = employee.address_id.name
            emp_barcode = employee.barcode
            emp_id = employee.id
            emp_hdmf = employee.hdmf_no
            emp_position = employee.job_id.name
            emp_bank_acc = employee.bank_account_id.acc_number
            
            details['EMP_HDMF_NUM'] = emp_hdmf
            details['EMP_NAME'] = emp_name
            details['EMP_FIRST'] = emp_first
            details['EMP_MIDDLE'] = emp_middle
            details['EMP_SURNAME'] = emp_surname
            details['EMP_ADDR'] = emp_addr or ''
            details['EMP_POS'] = emp_position or ''
            details['EMP_NUM'] = emp_barcode or ''
            details['EMP_BANK_ACC'] = emp_bank_acc or ''
            
            #default value of
            hr_salary_rule = self.env['hr.salary.rule'].search([])
            hr_salary_code = dict((code, 0) for code in hr_salary_rule.mapped('code'))
            details.update(hr_salary_code)

            results = get_hdmf_contribution(emp_id, date_from, date_to)
            
            details['MONTHLY_COMPENSATION'] = MONTHLY_COMPENSATION
            
            details['HDMF_EE'] = 0
            details['HDMF_ER'] = 0
            details['HDMF_TOTAL'] = 0
            
            if results:
                SUBTOTAL_HDMF_ER = 0
                SUBTOTAL_HDMF_EE = 0
                SUBTOTAL_HDMF = 0
                MONTHLY_COMPENSATION = 0
                
                for values in results:
                    SUBTOTAL_HDMF_ER += values.get('HDMFER-SM', 0.0) + values.get('HDMFER-M', 0.0)
                    SUBTOTAL_HDMF_EE += values.get('HDMF-SM', 0.0) + values.get('HDMF-M', 0.0)
                    MONTHLY_COMPENSATION += values.get('BASIC-SM',0.0) + values.get('BASIC-M',0.0)  + values.get('ClotAll-SM', 0.0) + \
                                            values.get('ClotAll-M', 0.0) + values.get('MedAll-SM', 0.0) + values.get('MedALl-M', 0.0) + \
                                            values.get('ConAll-SM', 0.0) + values.get('ConAll-M', 0.0) + values.get('DM-SM', 0.0) + values.get('DM-M', 0.0) + \
                                            values.get('MT-M', 0.0) + values.get('MT-SM', 0.0) + values.get('RiceSub-SM', 0.0) + values.get('RiceSub-M', 0.0) + values.get('EarNonTax',0.0)
                    
                    SUBTOTAL_HDMF +=  SUBTOTAL_HDMF_ER + SUBTOTAL_HDMF_EE
                
                TOTAL_HDMF += SUBTOTAL_HDMF_EE
                TOTAL_HDMFER += SUBTOTAL_HDMF_ER
                TOTAL_HDMF_CON += SUBTOTAL_HDMF
                
                details['HDMF_EE'] = SUBTOTAL_HDMF_EE
                details['HDMF_ER'] = SUBTOTAL_HDMF_ER
                details['HDMF_TOTAL'] = SUBTOTAL_HDMF 
                details['MONTHLY_COMPENSATION'] = MONTHLY_COMPENSATION
                    
            emp_hdmf_contribution.append(details)
            TOTAL_ROWS += 1

        emp_hdmf_contribution.append({
            'TOTAL_ROWS': TOTAL_ROWS,
            'TOTAL_HDMFER': TOTAL_HDMFER,
            'TOTAL_HDMF': TOTAL_HDMF,
            'TOTAL_HDMF_CON': TOTAL_HDMF_CON,
            'MONTHLY_COMPENSATION': MONTHLY_COMPENSATION
        })

        return emp_hdmf_contribution

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_hdmf_contribution_details = self.get_hdmf_contribution_details(data['form'])
        date_payroll = datetime.strptime(data['form'].get('date_payroll'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%b %d, %Y')
        date_to = datetime.strptime(data['form'].get('date_to'), '%Y-%m-%d').strftime('%b %d, %Y')
        company_id = (data['company_id'])
        company = self.env['res.company'].browse(company_id)

        details = get_hdmf_contribution_details[:-1]
        totals = get_hdmf_contribution_details[-1]

        dates = {
            'DATE_PAYROLL': date_payroll,
            'DATE_FROM': date_from,
            'DATE_TO': date_to
        }
        
        d = {
            'C_NAME' : company.name,
            'C_ADDRESS' : company.street,
            'C_ADDRESS2' : company.street2,
            'C_CITY' : company.city,
            'C_STATE' : company.state_id.name,
            'C_ZIP' : company.zip,
            'C_COUNTRY' : company.country_id.name,
            'C_PAGIBIG_NUM' : company.pagibig_num,
            }


        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_hdmf_contribution_details': details,
            'totals': totals,
            'dates': dates,
            'company_details' : d,

        }
        return self.env['report'].render('hris.report_hdmf_contribution_template', docargs)




