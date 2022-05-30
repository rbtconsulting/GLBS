# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class HrSalaryEmployee1601e(models.TransientModel):
    _name = 'hr.salary.employee.1601e'
    _description = 'Hr Salary Employee 1601e Report'

    def _get_default_start_date(self):
        start_date = fields.Date.from_string(fields.Date.today()).replace(month=1,day=1).strftime('%Y-%m-%d')
        return start_date

    start_date = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    employee_ids = fields.Many2many('hr.employee', 'payroll_bir_1601e_rel', 'payroll_bir_1601e_id', 'employee_id', string='Employees', required=True)
    percent_tax_witheld = fields.Float(string="% Witheld", required=True, digits=dp.get_precision('Discount'), default=8.0)

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

        return self.env['report'].get_action(self, 'hris.report_hrsalaryemployee1601e', data=data)
