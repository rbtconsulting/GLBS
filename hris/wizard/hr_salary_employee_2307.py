# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
    
class HRSalaryEmployee2307(models.TransientModel):
    _name = 'hr.salary.employee.2307'
    _description = 'Hr Salary Employee 2307 Report'

    def _get_default_start_date(self):
        start_date = fields.Date.from_string(fields.Date.today()).replace(month=1,day=1).strftime('%Y-%m-%d')
        return start_date

    def _get_default_end_date(self):
        _date = fields.Date.context_today(self)
        return _date 
    
    @api.onchange('atc_id')
    def onchange_atc(self):
        if self.atc_id:
            self.percent_tax_witheld = self.atc_id.tax_rate
            
    @api.model
    def create(self, vals):
        atc = self.env['alphanumeric.tax.code'].browse(vals.get('atc_id'))
        vals['percent_tax_witheld'] = atc.tax_rate
        return super(HRSalaryEmployee2307, self).create(vals)
    
    @api.multi
    def write(self, vals):
        atc = self.env['alphanumeric.tax.code'].browse(vals.get('atc_id') or self.atc_id.id)
        vals['percent_tax_witheld'] = atc.tax_rate
        return super(HRSalaryEmployee2307, self).write(vals)
    
    start_date = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    end_date = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    employee_ids = fields.Many2many('hr.employee', 'payroll_bir_2307_rel', 'payroll_bir_2307_id', 'employee_id', string='Employees', required=True)
    atc_type = fields.Selection([('ind', 'Individual'), ('corp', 'Corporate')], 'ATC Type', required=True)
    atc_id = fields.Many2one('alphanumeric.tax.code', 'ATC', required=True)
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'bir_2307_rule_rel', 'rule_id', 'bir_2307_id', 'Salary Rule')
    quarter = fields.Selection([
            ('first', '1st Quarter'),
            ('second', '2nd Quarter'),
            ('third', '3rd Quarter'),
            ('fourth', '4th Quarter')
        ],
        string='Quarter', required=True, 
        default='first'
    )
    percent_tax_witheld = fields.Float(string="% Witheld", required=True, digits=dp.get_precision('Discount'), default=0)

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

        return self.env['report'].get_action(self, 'hris.report_hrsalaryemployee2307', data=data)
