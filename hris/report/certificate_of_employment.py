#-*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models,fields


class ReportCertificateOfEmployment1(models.AbstractModel):
    _name = 'report.hris.report_employee_coe_template1'

    @api.model
    def render_html(self, docids, data=None):
        report = self.env['report']._get_report_from_name('hris.report_employee_coe_template1')
        model = report.model
        docs = self.env[model].browse(self._context.get('active_ids', []))
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        if 'date_to' in data['form'] and data['form'].get('date_to'):
            date_to = data['form'].get('date_to')
        else:
            date_to = fields.Date.context_today(self)
        date_to = datetime.strptime(date_to, '%Y-%m-%d').strftime('%B %d, %Y')

        dates  = {
             'date_start': date_from,
             'date_end': date_to,
        }

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'dates' : dates,
        }
        return self.env['report'].render('hris.report_employee_coe_template1', docargs)


class ReportCertificateOfEmployment2(models.AbstractModel):
    _name = 'report.hris.report_employee_coe_template2'

    @api.model
    def render_html(self, docids, data=None):
        report = self.env['report']._get_report_from_name('hris.report_employee_coe_template2')
        model = report.model
        docs = self.env[model].browse(self._context.get('active_ids', []))
        date_from = datetime.strptime(data['form'].get('date_from'), '%Y-%m-%d').strftime('%B %d, %Y')
        if 'date_to' in data['form'] and data['form'].get('date_to'):
            date_to = data['form'].get('date_to')
        else:
            date_to = fields.Date.context_today(self)
        date_to = datetime.strptime(date_to, '%Y-%m-%d').strftime('%B %d, %Y')

        dates  = {
             'date_start': date_from,
             'date_end': date_to,
        }

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'dates' : dates,
        }
        return self.env['report'].render('hris.report_employee_coe_template2', docargs)
