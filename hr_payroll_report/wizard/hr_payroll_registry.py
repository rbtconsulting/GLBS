# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import osv
import odoo.addons.decimal_precision as dp


class HrSalaryEmployee2307(models.TransientModel):

    _name = 'hr.payroll.registry'
    _description = 'HR Payroll Registry Report'

    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    date_payroll = fields.Date(string='Payroll Date', required=True, default=_get_default_end_date)
    date_from = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    date_to = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    employee_ids = fields.Many2many('hr.employee', 'payroll_registry_rel', 'payroll_registry_id', 'employee_id', string='Employees', required=True)
    #prepared_by = fields.Many2one('hr.employee', string='Prepared By', required=True)
    #approved_by = fields.Many2one('hr.employee', string='Approved By', required=True)
    #checked_by = fields.Many2one('hr.employee', string='Checked By', required=True)
    

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

        # id from hr_employee_bir_report.xml
        return self.env['report'].get_action(self, 'hr_payroll_report.report_hrpayrollregistry', data=data)
