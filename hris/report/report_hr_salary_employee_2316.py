# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ReportHRSalaryEmployee2316(models.AbstractModel):
    _name = 'report.hris.report_hrsalaryemployee2316'

    @api.model
    def get_year_to_date(self, form):
        employee_ids = form['employee_ids']
        employees = employee_ids and self.env['hr.employee'].browse(employee_ids)
        values = []
        date_from = form['start_date']
        end_date = form['end_date']
        domain = ['|',('active','=',True),('active','=',False)]
        generated_values = self.env['hr.annulization_structure.config'].generate_values(employees, date_from, end_date, 'bir-2316', domain)
        if not generated_values['values']:
            raise ValidationError(_('Year to Date has not been created!!'))
        return generated_values['values']

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        # get_employee_salary_details = self.get_employee_salary_details(data['form'])
        end_date_month = (data and data['form'].get('end_date')) and fields.Date.from_string(data['form']['end_date']).strftime('%m-%d') or False
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'value_dict': data and self.get_year_to_date(data['form']) or [],
            'start_date' : data and data['form'].get('start_date'),
            'end_date' : end_date_month,
        }
        return self.env['report'].render('hris.report_hrsalaryemployee2316_template', docargs)
    
