# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class HRSalaryEmployee2316(models.TransientModel):
    _name = 'hr.salary.employee.2316'
    _description = 'Hr Salary Employee 1601-C Report'

    def _get_default_start_date(self):
        start_date = fields.Date.from_string(fields.Date.today()).replace(month=1,day=1).strftime('%Y-%m-%d')
        return start_date

    def _get_default_end_date(self):
        end_date = fields.Date.from_string(fields.Date.today()).replace(month=12,day=31).strftime('%Y-%m-%d')
        return end_date

    start_date = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    end_date = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    employee_ids = fields.Many2many('hr.employee', 'payroll_bir_2316_rel', 'payroll_bir_2316_id', 'employee_id', string='Employees', required=True)

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
        return self.env['report'].get_action(self, 'hris.report_hrsalaryemployee2316', data=data)

