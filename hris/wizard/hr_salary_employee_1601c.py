# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class HrSalaryEmployee1601C(models.TransientModel):
    _name = 'hr.salary.employee.1601c'
    _description = 'Hr Salary Employee 1601-C Report'

    def _get_default_start_date(self):
        start_date = fields.Date.from_string(fields.Date.today()).replace(month=1,day=1).strftime('%Y-%m-%d')
        return start_date

    start_date = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    payout_from = fields.Many2one('hr.payroll.period_line', '1st Payout', required=True)
    payout_to = fields.Many2one('hr.payroll.period_line', '2nd Payout', required=True)
    employee_ids = fields.Many2many('hr.employee', 'payroll_bir_1601c_rel', 'payroll_bir_1601c_id', 'employee_id', string='Employees', required=True)
    date_release_from = fields.Date('Date Release')
    date_release_to = fields.Date('Date Release')
    for_month = fields.Date('For the Month')
    adjustment_taxes = fields.Float('Adjustment of Taxes Withheld from previous month/s')
    previously_field_tax = fields.Float('Tax Remitted in Return Previously Filed')
    remittances_specify = fields.Char('Other Remittances Made(specify)')
    remittances_amount = fields.Float('Amount')
    non_taxable_specify = fields.Char('Other Non-Taxable Compensation (specify)')
    non_taxable_amount = fields.Float('Amount')

    @api.onchange('payout_from','payout_to')
    def onchange_payroll_period(self):
        if self.payout_from:
            self.date_from = self.payout_from.start_date
            self.date_to = self.payout_from.end_date
            self.date_release_from = self.payout_from.date_release
        if self.payout_from and self.payout_to:
            self.date_from = self.payout_from.start_date
            self.date_to = self.payout_to.end_date
            self.date_release_to = self.payout_to.date_release

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
        return self.env['report'].get_action(self, 'hris.report_hrsalaryemployee1601c', data=data)
    
    
#     surcharge = fields.Integer('Surcharge',size = 13)
#     interest = fields.Integer('Interest',size = 13)
#     compromise = fields.Integer('Compromise', size=13)
#     tax_remit = fields.Integer('Tax Remitted(21A)' , size=11)
#     other_pay = fields.Integer('Other Payments Made(21B)', size=11)
#     previous_mnth = fields.Date(string='Previous Month')
#     date_paid = fields.Date(string="Date Paid")
    amended_return = fields.Boolean(string='Amended Return?')
    any_taxes_witheld = fields.Boolean(string='Any Taxes Witheld?')
    tax_treaty = fields.Boolean(string='Are these payees availing of tax relief under Special Law International Tax Treaty?')
    specify = fields.Text('If yes, specify')
    category_of_agent = fields.Selection([('private', 'Private'),
                                    ('government', 'Government')],string='Category of Witholding agent')#     bank_code = fields.Char('Bank Code', size =13)
#     tax_pd = fields.Integer('Tax Paid for the month', size =13 )
#     tax_due = fields.Integer('Should be Tax Due for the Month', size=13)
#     frm_curr_yr = fields.Integer('From Current Year',size=11)
#     frm_end = fields.Integer('From Year End',size=11)
