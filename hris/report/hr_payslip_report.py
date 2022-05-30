#-*- coding:utf-8 -*-

from odoo import api, models,fields
#from odoo import tools
from datetime import timedelta

class PayslipDetailsReportTemplateTwo(models.AbstractModel):
        _name = 'report.hris.report_payslipdetails_template_two'
        
        @api.multi
        def get_days(self, employee_id, holiday_status_id, args=[]):
            """Returns the leaves computation."""
            # need to use `dict` constructor to create a dict per id
            
            result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0, virtual_remaining_leaves=0)) for id in [holiday_status_id.id])
            
            domain = [
                ('employee_id', '=', employee_id),
                ('state', 'in', ['confirm', 'validate1', 'validate']),
                ('holiday_status_id', '=', holiday_status_id.id)
            ]
            if args:
                domain += args
                
            holidays = self.env['hr.holidays'].search(domain)
    
            for holiday in holidays:
                status_dict = result[holiday.holiday_status_id.id]
                if holiday.type == 'add':
                    if holiday.state == 'validate':
                        # note: add only validated allocation even for the virtual
                        # count; otherwise pending then refused allocation allow
                        # the employee to create more leaves than possible
                        status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                        status_dict['max_leaves'] += holiday.number_of_days_temp
                        status_dict['remaining_leaves'] += holiday.number_of_days_temp
                elif holiday.type == 'remove':  # number of days is negative
                    status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                    if holiday.state == 'validate':
                        status_dict['leaves_taken'] += holiday.number_of_days_temp
                        status_dict['remaining_leaves'] -= holiday.number_of_days_temp
            return result
        
        def get_leave_balances(self, employee_id):
            """Returns  employee leave balances."""
            res = self.env['hr.payslip.template'].search([], limit=1)
            holiday_status  = res.holiday_status_ids
            results = []
            
            for holiday in holiday_status:
                leave_types = {}
                leave_types['name'] = holiday.name 
                leave_types['balance'] = self.get_days(employee_id.id, holiday)[holiday.id]['remaining_leaves'] 
                results.append(leave_types)
            
            return results
        
        def get_leaves_taken(self, employee_id, payslip):
            """Returns  employee leaves taken."""
            res = self.env['hr.payslip.template'].search([], limit=1)
            holiday_status  = res.holiday_status_ids
            results = []
            
            date_f = fields.Datetime.from_string(payslip.date_from)
            date_t = fields.Datetime.from_string(payslip.date_to)

            date_from = date_f.replace(hour=0, minute=0, second=0, microsecond=0)
            #end_dt = date_t.replace(hour=23, minute=59, second=59, microsecond=999999)
            date_to = date_t.replace(hour=7, minute=0, second=59, microsecond=999999) + timedelta(days=1)
            
            args = [
                ('date_approved', '>=', fields.Datetime.to_string(date_from)),
                ('date_approved', '<=', fields.Datetime.to_string(date_to))
                ]
            for holiday in holiday_status:
                leave_types = {}
                leave_types['name'] = holiday.name 
                leave_types['used'] = self.get_days(employee_id.id, holiday, args)[holiday.id]['leaves_taken'] 
                results.append(leave_types)
            
            return results
        
        def get_earnings(self):
            """Returns the salary code belong to earnings column"""
            res = self.env['hr.payslip.template'].search([], limit=1)
            return [record.code for record in res.salary_rule_earnings]
            
        def get_deductions(self):
            """Returns the salary code belong to deductions column"""
            res = self.env['hr.payslip.template'].search([], limit=1)
            return [record.code for record in res.salary_rule_deductions]
            
        def get_loans(self):
            """Returns the salary code belongs to loans column"""
            res = self.env['hr.payslip.template'].search([], limit=1)
            return [record.code for record in res.salary_rule_loans]
        
        def get_earning_inputs(self):
            """Returns the code belongs to earning inputs column"""
            res = self.env['hr.payslip.template'].search([], limit=1)
            return [record.code for record in res.salary_rule_earning_inputs]
        
        def get_deduction_inputs(self):
            """Returns the code belongs to deductions inputs column"""
            res = self.env['hr.payslip.template'].search([], limit=1)
            return [record.code for record in res.salary_rule_deduction_inputs]
        
        @api.model
        def render_html(self, docids, data=None):
            payslips = self.env['hr.payslip'].browse(docids)
            res = self.env['hr.payslip.template'].search([], limit=1)
            
            docargs = {
                'doc_ids': docids,
                'doc_model': 'hr.payslip',
                'docs': payslips,
                'data': data,
                'remaining_leaves': self.get_leave_balances,
                'leaves_taken': self.get_leaves_taken,
                'earnings_code': self.get_earnings(),
                'deductions_code': self.get_deductions(),
                'loans_code': self.get_loans(),
                'earning_inputs_code': self.get_earning_inputs(),
                'deduction_inputs_code': self.get_deduction_inputs()
            }
            
            return self.env['report'].render(res.report_template_id.report_name, docargs)
            