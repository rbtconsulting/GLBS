# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, models


class SalaryRuleInput(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(SalaryRuleInput, self).get_inputs(contract_ids, date_from, date_to)

        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0]).employee_id.name
        adv_salary = self.env['salary.advance'].search([('employee_id','=',emp_id)])

        for each_employee in adv_salary:
            current_date = datetime.strptime(date_from, '%Y-%m-%d').date().month
            date = self.env['salary.advance'].browse(each_employee.id).date
            existing_date = datetime.strptime(date, '%Y-%m-%d').date().month
            if current_date == existing_date:
                adv_browse = self.env['salary.advance'].browse(each_employee.id)
                state = adv_browse.state
                amount = adv_browse.advance
                for result in res:
                    if state == 'approved' and amount != 0 and result.get('code') == 'SAR':
                        result['amount'] = amount
        return res
