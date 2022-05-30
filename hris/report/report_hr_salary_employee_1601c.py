# -*- coding:utf-8 -*-

from datetime import datetime, date

from odoo import api, models, fields
from dateutil.relativedelta import relativedelta


class ReportHrSalaryEmployee1601C(models.AbstractModel):
    _name = 'report.hris.report_hrsalaryemployee1601c'

    @api.model
    def get_payslips(self, form):
        employee_ids = form['employee_ids']
        for_month = form['for_month']
        start_date = form['date_release_from']
        end_date = form['date_release_to']
        category_of_agent = form['category_of_agent']
        amended_return = form['amended_return']
        any_taxes_witheld = form['any_taxes_witheld']
        tax_treaty = form['tax_treaty']
        specify = form['specify']
        adjustment_taxes = form['adjustment_taxes']
        previously_field_tax = form['previously_field_tax']
        remittances_specify = form['remittances_specify']
        remittances_amount = form['remittances_amount']
        non_taxable_specify = form['non_taxable_specify']
        non_taxable_amount = form['non_taxable_amount']

        pay = employee_ids and self.env['hr.payslip'].search([('employee_id', 'in', employee_ids),
                                                              ('credit_note','=',False),
                                                              '|', ('date_release', '=', start_date),
                                                              ('date_release', '=', end_date)])
        item_config = self.env['bir.1601c.report.config'].search([])
        values = {}
        for item in item_config:
            if item.earner_type:
                payslips = pay.filtered(lambda l: l.employee_id.contract_id.earner_type == item.earner_type)
            else:
                payslips = pay

            total = sum(payslips.mapped('line_ids').filtered(
                lambda l: l.salary_rule_id in item.mapped('salary_rule_ids')).mapped('total'))
            total = total or 0
            if values.get(str(item.code)):
                values.update({str(item.code): total + values[str(item.code)]})
            else:
                values.update({str(item.code): total})

        employees = employee_ids and self.env['hr.employee'].browse(employee_ids) or self.env['hr.employee']
        if employees:
            company_id = employees[0].id_company
            company_addr = ",".join(filter(lambda r: r != '', [company_id.street or '',
                                                               company_id.street2 or '',
                                                               company_id.city or '',
                                                               company_id.state_id.name or '',
                                                               company_id.country_id.name or '']))
        else:
            company_addr = ""
        values.update({
            '20': (values.get('20') or 0),
        })
        values.update({
            'employees': employees and employees[0] or employees,
            'company_addr': company_addr,
            '1': for_month and fields.Date.from_string(for_month).strftime('%m/%Y'),
            '2': amended_return,
            '3': any_taxes_witheld,
            '6': employees and employees[0].id_company.vat or False,
            '7': employees and employees[0].id_company.rdo_code,
            '8': employees and employees[0].id_company.name or False,
            '9A': employees and employees[0].id_company.zip or False,
            '10': employees and employees[0].id_company.phone or False,
            '11': category_of_agent,
            '12': employees and employees[0].id_company.email or False,
            '13': tax_treaty,
            '13A': specify,
            '20A': non_taxable_specify,
            '21': ((values.get('15') or 0) + (values.get('16') or 0) + (values.get('17') or 0) +
                   (values.get('18') or 0) + (values.get('19') or 0) + (values.get('20') or 0)),
            '26': adjustment_taxes or 0,
            '27': (values.get('25') or 0) + (adjustment_taxes or 0),
            '28': previously_field_tax or 0,
            '29A': remittances_specify or '',
            '29': remittances_amount or 0,
            '35': (values.get('32') or 0) + (values.get('33') or 0) + (values.get('34') or 0),
        })
        values.update({
            '22': (values.get('14') or 0) - (values.get('21') or 0),
            '30': (values.get('28') or 0) + (values.get('29') or 0),
        })
        values.update({
            '24': (values.get('22') or 0) - 0,
            '31': (values.get('27') or 0) - (values.get('30') or 0),
            '36': (values.get('35') or 0) + ((values.get('27') or 0) - (values.get('30') or 0)),
        })
        return values

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        values = data and self.get_payslips(data['form']) or {}

        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'values': dict(values),
        }
        return self.env['report'].render('hris.report_hrsalaryemployee1601c_template', docargs)
