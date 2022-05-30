# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, fields, models,tools


class HrPayslipReport(models.TransientModel):
    _name = 'hr.payslip.report'

    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    start_date = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    end_date = fields.Date(string='End Date', required=True, default=_get_default_start_date)
    employee_ids = fields.Many2many('hr.employee', 'payroll_payslip_rel', 'payroll_payslip_id', 'employee_id',
                                    string='Employees', required=True)


    @api.multi
    def print_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env['report'].get_action(self, 'hris.report_payslip_template', data=data)

