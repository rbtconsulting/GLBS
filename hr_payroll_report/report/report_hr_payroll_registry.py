# -*- coding:utf-8 -*-

from datetime import datetime, date

from odoo import api, models
from odoo.osv import osv

class ReportHrSalaryEmployee2307(models.AbstractModel):
    _name = 'report.hr_payroll_report.report_hrpayrollregistry'

    def get_payroll_registry_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_payroll = form.get('date_payroll', None)
        date_from = form.get('date_from', None)
        date_to = form.get('date_to', None)

        employees = self.env['hr.employee'].browse(emp_ids)

        dt_payroll = datetime.strptime(date_payroll, '%Y-%m-%d')
        dt_from = datetime.strptime(date_from, '%Y-%m-%d')
        dt_to = datetime.strptime(date_to, '%Y-%m-%d')


        def format_date(str_date):
            dt = datetime.strptime(str_date, '%Y-%m-%d')
            year, mnth, day = dt.year, dt.month, dt.day

            day = '0' + str(day) if len(str(day)) == 1 else day
            mnth = '0' + str(mnth) if len(str(mnth)) == 1 else mnth
            return '-'.join([str(mnth), str(day), str(year)])

        def get_payslip_lines(emp_id, date_from, date_to):
            payslip_lines = """
                SELECT pl.code, sum(pl.total)
                FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
                LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                WHERE to_char(p.date_from, 'mm-dd-yyyy') = '{}' AND to_char(p.date_to, 'mm-dd-yyyy') = '{}'
                AND p.state = 'done' AND p.employee_id = {}
                GROUP BY pl.code, he.name_related
                ORDER BY he.name_related
            """.format(date_from, date_to, emp_id)

            self.env.cr.execute(payslip_lines)

            d = self.env.cr.fetchall()

            if d:
                return [dict(d)]
            return []

        def get_worked_days_lines(emp_id, date_from, date_to):
            worked_days_lines = """
                SELECT w.code, sum(w.number_of_hours)
                FROM hr_payslip_worked_days AS w
                LEFT JOIN hr_payslip AS p ON w.payslip_id=p.id
                LEFT JOIN hr_employee AS he ON he.id = p.employee_id
                WHERE to_char(p.date_from, 'mm-dd-yyyy') = '{}' AND to_char(p.date_to, 'mm-dd-yyyy') = '{}'
                AND p.state = 'done' AND p.employee_id = {}
                GROUP BY w.code, he.name_related
                ORDER BY he.name_related
            """.format(date_from, date_to, emp_id)

            self.env.cr.execute(worked_days_lines)

            d = self.env.cr.fetchall()

            if d:
                return [dict(d)]
            return []

        emp_payroll_registry = []

        # worked_hours
        TOTAL_DTR = 0.00

        # payslip_lines
        totals = []
        TOTAL_BASIC = 0.00
        TOTAL_OT = 0.00
        TOTAL_NSD = 0.00
        TOTAL_GROSS = 0.00
        TOTAL_NET = 0.00
        TOTAL_ROWS = 0
        TOTAL_UP = 0.00
        TOTAL_WTsemi = 0.00
        TOTAL_SSS = 0.00
        TOTAL_PH = 0.00
        TOTAL_PAGIBIG = 0.00

        """
            Initialize other totals here
        

            EMPLOYEE NUMBER 
            NAME    
            BANK ACCOUNT    
            POSITION    
            
            BASIC PAY => BASIC   
            TOTAL WORKED HOURS => DTR 
            TOTAL OVERTIME  => OT
            TOTAL NIGHT DIFFERENTIAL => NSD     
            TOTAL LEAVE/OFFICIAL BUSINESS   
            TOTAL LEAVE W/O PAY 
            TOTAL UNDERTIME/TARDINESS => UTIME 
            TOTAL ABSENCES  => UP
            ADJUSTMENT  
            OTHER INCOME    
            SSS => SSS
            PHIC => PH    
            HDMF => PAGIBIG   
            GROSS TAXABLE INCOME =>    
            WITHHOLDING TAX => WT
            OTHER DEDUCTIONS    
            NET PAY => NET
        """
        for employee in employees:
            d = {}            
            emp_name = employee.name
            emp_addr = employee.address_id.name
            emp_id = employee.id
            emp_position = employee.job_id.name
            # Add tax code here
            """
                splucena
                Add additional employee details here
                Add additional employee details to dictionary
            """
            d.update({
                'EMP_NAME': emp_name or '',
                'EMP_ADDR': emp_addr or '',
                'EMP_POS': emp_position or '',
                'EMP_NUM': emp_id, # TEMPORARY REPLACE WITH ACTUAL FIELD IN PRODUCTION
                # Update to include tax code
            })

            res_payslip_lines = get_payslip_lines(emp_id, format_date(date_from), format_date(date_to))
            if res_payslip_lines:                
                LEN_LS_ITEMS = len(res_payslip_lines)
                for gpr in res_payslip_lines:
                    TOTAL_BASIC += gpr.get('BASIC', 0.00)
                    TOTAL_OT += gpr.get('OT', 0.00)
                    TOTAL_NSD += gpr.get('NSD', 0.00)
                    TOTAL_NET += gpr.get('NET', 0.00)
                    TOTAL_GROSS += gpr.get('GROSS', 0.00)
                    TOTAL_UP += abs(gpr.get('UP', 0.00))
                    TOTAL_WTsemi += gpr.get('WTsemi', 0.00)
                    TOTAL_SSS += gpr.get('SSS', 0.00)
                    TOTAL_PH += gpr.get('PH', 0.00)
                    TOTAL_PAGIBIG += gpr.get('PAGIBIG', 0.00)
                    d.update(gpr)

            if not d.get('BASIC'):
                d.update({
                    'BASIC': 0.00, 
                })
            if not d.get('OT'):
                d.update({
                    'OT': 0.00, 
                })
            if not d.get('NSD'):
                d.update({
                    'NSD': 0.00, 
                })
            if not d.get('NET'):
                d.update({
                    'NET': 0.00, 
                })
            if not d.get('GROSS'):
                d.update({
                    'GROSS': 0.00, 
                })
            if not d.get('WTsemi'):
                d.update({
                    'WTsemi': 0.00, 
                })
            if not d.get('UP'):
                d.update({
                    'UP': 0.00, 
                })
            if not d.get('SSS'):
                d.update({
                    'SSS': 0.00, 
                })
            if not d.get('PH'):
                d.update({
                    'PH': 0.00, 
                })
            if not d.get('PAGIBIG'):
                d.update({
                    'PAGIBIG': 0.00, 
                })            

            res_worked_days_lines = get_worked_days_lines(emp_id, format_date(date_from), format_date(date_to))
            if res_worked_days_lines:
                for worked_days_line in res_worked_days_lines:
                    TOTAL_DTR += worked_days_line.get('DTR', 0.00)
                    d.update(worked_days_line)

            if not d.get('DTR'):
                d.update({
                    'DTR': 0.00
                })

            emp_payroll_registry.append(d)
            TOTAL_ROWS += 1

        emp_payroll_registry.append({
            'TOTAL_NET': TOTAL_NET,
            'TOTAL_GROSS': TOTAL_GROSS,
            'TOTAL_BASIC': TOTAL_BASIC,
            'TOTAL_OT': TOTAL_OT,
            'TOTAL_NSD': TOTAL_NSD,
            'TOTAL_ROWS': TOTAL_ROWS,
            'TOTAL_UP': TOTAL_UP,
            'TOTAL_WTsemi': TOTAL_WTsemi,
            'TOTAL_SSS': TOTAL_SSS,
            'TOTAL_PH': TOTAL_PH,
            'TOTAL_PAGIBIG': TOTAL_PAGIBIG,
            'TOTAL_DTR': TOTAL_DTR
        })

        return emp_payroll_registry

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_payroll_registry_details = self.get_payroll_registry_details(data['form'])
        date_payroll = datetime.strptime(data['form'].get('date_payroll'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        date_to = datetime.strptime(data['form'].get('date_to'), '%Y-%m-%d').strftime('%B %d, %Y')
        #get_signatories = self.get_signatories(data['form'])

        #print get_payroll_registry_details

        details = []
        totals = []

        #for record in get_payroll_registry_details:
        #    details.append(record[0])
        #    details.append(record[1])
            #if record:
            #    details.append(record[0])
            #    details.append(record[1])
            #print record
            

        #print details, totals
        #print get_payroll_registry_details
        total_record = len(get_payroll_registry_details) - 1
        for index, record in enumerate(get_payroll_registry_details):
            if index != total_record:
                details.append(record)
            else:
                totals.append(record)



        dates = {
            'DATE_PAYROLL': date_payroll,
            'DATE_FROM': date_from,
            'DATE_TO': date_to
        }

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_payroll_registry_details': details,
            'totals': totals,
            'dates': dates,
            #'get_signatories': get_signatories
        }
        return self.env['report'].render('hr_payroll_report.report_hrpayrollregistry_template', docargs)
    