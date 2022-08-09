# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models, fields

class ReportHRPayrollRegistry(models.AbstractModel):
    _name = 'report.hris.report_hrpayrollregistry_template'

    def get_payroll_registry_details(self, form):
        emp_ids = form.get('employee_ids', [])
        date_release_from = form.get('date_release_from',None)
        date_release_to = form.get('date_release_from',None)
        period_id_from = form['payroll_period_from_id'][0]
        period_id_to = form.get('payroll_period_to_id',None)
        period_from = self.env['hr.payroll.period_line'].browse(period_id_from)
        period_to = period_id_to and self.env['hr.payroll.period_line'].browse(period_id_to[0])
        date_from = period_from.start_date
        date_to = period_to and period_to.end_date or period_from.end_date

        employees = self.env['hr.employee'].browse(emp_ids)

        def format_date(str_date):
            dt = datetime.strptime(str_date, '%Y-%m-%d')
            year, mnth, day = dt.year, dt.month, dt.day

            day = '0' + str(day) if len(str(day)) == 1 else day
            mnth = '0' + str(mnth) if len(str(mnth)) == 1 else mnth
            return '-'.join([str(mnth), str(day), str(year)])


#         def get_worked_days_lines(emp_id, date_from, date_to):
#             worked_days_lines = """SELECT worked_hours.code, 
#                 sum(worked_hours.total_hours) as total_hours FROM((
#                     SELECT w.code, sum(w.number_of_hours) as total_hours
#                 FROM hr_payslip_worked_days AS w
#                 LEFT JOIN hr_payslip AS p ON w.payslip_id=p.id
#                 LEFT JOIN hr_employee AS he ON he.id = p.employee_id
#                 WHERE to_char(p.date_from, 'mm-dd-yyyy') >= '{}' AND to_char(p.date_to, 'mm-dd-yyyy') <= '{}'
#                 AND p.credit_note=False AND p.employee_id = {}
#                 GROUP BY w.code, he.name_related 
#                 ORDER BY he.name_related)
#              UNION ( SELECT w.code, -sum(w.number_of_hours) total_hours
#                     FROM hr_payslip_worked_days AS w
#                     LEFT JOIN hr_payslip AS p ON w.payslip_id=p.id
#                     LEFT JOIN hr_employee AS he ON he.id = p.employee_id
#                     WHERE to_char(p.date_from, 'mm-dd-yyyy') >= '{}' AND to_char(p.date_to, 'mm-dd-yyyy') <= '{}'
#                     AND p.credit_note=True AND p.employee_id = {}
#                     GROUP BY w.code, he.name_related 
#                     ORDER BY he.name_related)
#                 ) worked_hours GROUP BY worked_hours.code
#                 """.format(date_from, date_to, emp_id, date_from, date_to, emp_id)
# 
#             self._cr.execute(worked_days_lines)
#             res = self._cr.fetchall()
#             if res:
#                 return [dict(res)]
#             return []

        emp_payroll_registry = []
        total_list = {}

        # payslip_lines
        TOTAL_BASIC = 0
        TOTAL_BASIC = 0
        TOTAL_DED = 0
        domain = [('employee_id','in', employees.ids),('credit_note','=', False),('date_from', '>=', date_from),
                    ('date_to','<=', date_to), ('state', 'in', ['draft', 'done'])]
        payslips = self.env['hr.payslip'].search(domain)
        for employee in employees:
            results = {}
            results['EMPLOYEE'] = employee
#             hr_salary_rule = self.env['hr.salary.rule'].search([])
#             hr_salary_code = dict((code, 0) for code in hr_salary_rule.mapped('code'))

            payslip_ids = payslips.filtered(lambda p: p.employee_id == employee)
            payslip_lines = payslip_ids.mapped('line_ids')
            results['BASIC'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.BSC')]).mapped('amount')) or 0.0
            results['LOAN'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.LON')]).mapped('amount')) or 0.0
            results['OTHER_TAX_INCOME'] = payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.OtherTaxInc')])
            results['OTHER_NONTAX_INCOME'] = payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.ONTXINC')])
            results['OTHER_TAX_DEDUCT'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.OtherTaxDed')]).mapped('amount')) or 0.0
            results['OTHER_NONTAX_DEDUCT'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.ONTXDED')]).mapped('amount')) or 0.0
            results['employee_contribution'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.EMPCTRB')]).mapped('amount')) or 0.0
            results['withholding_tax'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.WTX')]).mapped('amount')) or 0.0
            results['deduction'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hr_payroll.DED')]).mapped('amount')) or 0.0
            results['net_pay'] = sum(payslip_lines.filtered(lambda l: l.category_id in [self.env.ref('hris.FNP')]).mapped('amount')) or 0.0
            results['total_earnings'] = (results['BASIC'] + (sum(results['OTHER_TAX_INCOME'].mapped('amount')) or 0.0) +
                                         (sum(results['OTHER_NONTAX_INCOME'].mapped('amount')) or 0.0))
            emp_payroll_registry.append(results)
            TOTAL_BASIC += results['BASIC']
            TOTAL_DED += (results['deduction'] + results['withholding_tax'] + results['LOAN'] + results['employee_contribution']
                            + results['OTHER_TAX_DEDUCT'] + results['OTHER_NONTAX_DEDUCT'])

        total_list['total_emp'] = len(employees)
        total_list['total_salary'] = TOTAL_BASIC
        total_list['total_comensation'] = TOTAL_BASIC
        total_list['total_deductions'] = TOTAL_DED
        total_list['total_net_salary'] = TOTAL_BASIC - TOTAL_DED
        return emp_payroll_registry, total_list

#             res_payslip_lines = get_payslip_lines(employee.id, format_date(date_from), format_date(date_to))
#             BASIC = 0
#             REGWRK = 0
#             WTAX = 0
#             OT = 0
#             UT_TD = 0
#             ABS = 0
#             NSD = 0
#             NightDiff = 0
#             GROSS = 0
#             HDMF = 0
#             PHIC = 0
#             SSS = 0
#             NTP = 0
#             FNP = 0
#             LWOP = 0
#             LWP = 0
#             SAR = 0
#             EARTAX = 0
#             EARNONTAX = 0
#             DEDTAX= 0
#             DEDNONTAX = 0
#             DM = 0
#             CLOTALL = 0
#             MEDALL = 0
#             CONALL = 0
#             MT = 0
#             RICESUB = 0
#             OTHER_INCOME = 0
#             LOAN = 0
# 
# 
#             earning_dict = []
#             deduct_dict = []
#             ntp_dict = []
#             if res_payslip_lines:                
#                 for gpr in res_payslip_lines:
#                     BASIC += gpr.get('BASIC-M', 0.0)
#                     BASIC += gpr.get('BASIC-SM', 0.0)
#                     BASIC += gpr.get('BASIC', 0.0)
#                     
#                     LOAN += gpr.get('SSSLOAN', 0.0)
#                     LOAN += gpr.get('HDMFLOAN', 0.0)
#                     
#                     OT += gpr.get('RegOT', 0.0)
#                     OT += gpr.get('RestOT', 0.0)
#                     OT += gpr.get('RegHolOT', 0.0)
#                     OT += gpr.get('SpeHolOT', 0.0)
#  
#  
#                     NightDiff += gpr.get('NightDiff', 0.0)
#                     NightDiff += gpr.get('NightShiftDiff', 0.0)
#  
#                     FNP += gpr.get('FNP', 0.0)
#                      
#                     GROSS += gpr.get('GROSS', 0.0)
#                     NTP += gpr.get('NTP', 0.0)
#                     
#                     ABS += abs(gpr.get('ABS', 0.0))
#                     ABS += abs(gpr.get('INSTALL', 0.0))
#                     ABS += abs(gpr.get('SAR', 0.0))
#                     UT_TD += abs(gpr.get('UT', 0.0))
#                     UT_TD += abs(gpr.get('TD', 0.0))
#                     
#                     WTAX += gpr.get('WTHTAX-M', 0.0)
#                     WTAX += gpr.get('WTHTAX-SM', 0.0)
#                     
#                     SSS += gpr.get('SSS-M', 0.0)
#                     SSS += gpr.get('SSS-SM', 0.0)
#                     
#                     PHIC += gpr.get('PHIC-SM', 0.0)
#                     PHIC += gpr.get('PHIC-M', 0.0)
#                     
#                     HDMF += gpr.get('HDMF-SM', 0.0)
#                     HDMF += gpr.get('HDMF-M', 0.0)
#                     
#                     EARTAX += gpr.get('EarTax', 0.0)
#                     EARNONTAX += gpr.get('EarNonTax',0.0)
#                     DEDTAX += gpr.get('DedTax',0.0)
#                     DEDTAX += gpr.get('hd',0.0)
#                     DEDNONTAX += gpr.get('DedNonTax',0.0)
#                     DEDNONTAX += gpr.get('CA',0.0)
# 
#                     CLOTALL += gpr.get('ClotAll-SM',0.0)
#                     CLOTALL += gpr.get('ClotAll-M',0.0)
#                     MEDALL += gpr.get('MedAll-SM',0.0)
#                     MEDALL += gpr.get('MedALl-M',0.0)
#                     CONALL += gpr.get('ConAll-SM',0.0)
#                     CONALL += gpr.get('ConAll-M',0.0)
#                     DM     += gpr.get('DM-SM',0.0)
#                     DM     += gpr.get('DM-SM',0.0)
#                     MT     += gpr.get('MT-M',0.0)
#                     MT += gpr.get('MT-SM', 0.0)
#                     RICESUB += gpr.get('RiceSub-SM',0.0)
#                     RICESUB += gpr.get('RiceSub-M',0.0)
# 
#                     OTHER_INCOME = CLOTALL + MEDALL + CONALL + DM + MT + RICESUB
# 
#                     earning_dict.append({'amount': BASIC})
#                     deduct_dict.append({'l_amount': LOAN})
#                     deduct_dict.append({'d_amount': DEDTAX})
#                     deduct_dict.append({'dn_amount': DEDNONTAX})
#                     deduct_dict.append({'employees_amount': SSS + PHIC + HDMF})
#                     deduct_dict.append({'w_amount': WTAX})
#                     deduct_dict.append({'a_amount': ABS + UT_TD})
#                     deduct_dict.append({'total_deduction': ABS + UT_TD + WTAX + LOAN + DEDTAX + DEDNONTAX + SSS + PHIC + HDMF})
#                     earning_dict.append({'total_earning': BASIC})
#                     ntp_dict.append({'ntp': FNP, 'total_ntp': FNP})
# 
#                 results['earnings'] = earning_dict
#                 results['deduction'] = deduct_dict
#                 results['netpay'] = ntp_dict
# 
#                 TOTAL_BASIC += results['BASIC']
#                 TOTAL_DED += (results['deduction'] + results['withholding_tax'] + results['LOAN'] + results['employee_contribution']
#                                 + results['OTHER_TAX_DEDUCT'] + results['OTHER_NONTAX_DEDUCT'])
#                 
#                 TOTAL_LOAN += LOAN
#                 TOTAL_OT += OT
#                 TOTAL_ABS += ABS
#                 TOTAL_UT_TD += UT_TD
#                 TOTAL_NSD += NSD
# 
#                 TOTAL_NIGHTDIFF += NightDiff
#                 TOTAL_SSS += SSS
#                 TOTAL_HDMF += HDMF
#                 TOTAL_PHIC += PHIC
#                 
#                 TOTAL_GROSS += GROSS
#                 TOTAL_NTP += NTP
#                 TOTAL_WTAX += WTAX
#                 TOTAL_FNP += FNP
# 
#                 TOTAL_EARTAX += EARTAX
#                 TOTAL_EARNONTAX += EARNONTAX
#                 TOTAL_DEDTAX += DEDTAX
#                 TOTAL_DEDNONTAX += DEDNONTAX
# 
#                 TOTAL_OTHER_INCOME += OTHER_INCOME
#                 TOTAL_OTHER_INCOME_NONTAX = TOTAL_OTHER_INCOME + TOTAL_EARNONTAX
#                 
# #             res_worked_days_lines = get_worked_days_lines(employee.id, date_from, date_to)
# #             if res_worked_days_lines:
# #                 REGWRK = 0
# #                 for worked_days_line in res_worked_days_lines:
# #                     
# #                     REGWRK += worked_days_line.get('RegWrk', 0.0)
# #                     REGWRK += worked_days_line.get('NightShiftWrk', 0.0)
# #                     REGWRK += worked_days_line.get('RestDayWrk', 0.0)
# #                     REGWRK += worked_days_line.get('RegHolWrk', 0.0)
# #                     REGWRK += worked_days_line.get('SpeHolWrk', 0.0)
# # 
# #                 TOTAL_REGWRK += REGWRK
# 
#             emp_payroll_registry.append(results)
# 
#             TOTAL_ROWS += 1
# 
#         total_list['total_emp'] = len(employees)
#         total_list['total_salary'] = TOTAL_BASIC
#         total_list['total_comensation'] = TOTAL_BASIC
#         total_list['total_deductions'] = TOTAL_DED
#         total_list['total_net_salary'] = TOTAL_BASIC - TOTAL_DED
#         return emp_payroll_registry, total_list

    def get_form_data(self, form):
        payroll_period_id = form.get('payroll_period_from_id', False)[1]

        form_data = {
            'PAYROLL_PERIOD': payroll_period_id,
        }

        return form_data

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_payroll_registry_details, total_detail = self.get_payroll_registry_details(data['form'])
        date_release = datetime.strptime(data['form'].get('date_release_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        form_data = self.get_form_data(data['form'])

#         details = []
#         totals = []

        #print details, totals
        #print get_payroll_registry_details
#         total_record = len(get_payroll_registry_details)
#         for index, record in enumerate(get_payroll_registry_details):
#             if index != total_record:
#                 details.append(record)
#             else:
#                 totals.append(record)


        dates = {'DATE_RELEASE': date_release}
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_payroll_registry_details': get_payroll_registry_details,
            'totals': total_detail,
            'dates': dates,
            'form_data': form_data
        }

        return self.env['report'].render('hris.report_hrpayrollregistry_template', docargs)
    