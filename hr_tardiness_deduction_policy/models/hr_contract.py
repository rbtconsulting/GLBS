# -*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.tools.translate import _

from odoo.tools import float_round


class HRContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def get_tardiness_deduction(self, payslip, contract, late_hours, code):
	self = self.sudo()
	payslip_object = self.env['hr.payslip'].browse(payslip.id)
        rules = self.env['hr.salary.rule'].search([('code', '=', code)], limit=1)
        amount_to_deduct = 0.0
        if rules.is_tardiness_policy:
            employee_attendance = payslip_object.get_worked_hour_lines(payslip_object.employee_id.id, payslip.date_from, payslip.date_to)
            employee_min_rate = self.env['hr.salary.move'].search([('contract_id', '=', contract.id)], limit=1)
            min_rate = employee_min_rate.hourly_rate / 60.00

            for record in employee_attendance:

                late_hours = record.late_hours * 60
                domain = [('range1', '<=', late_hours), ('range2', '>=', late_hours)]
                object = self.env['tardiness.table'].search(domain, limit=1)
                equivalent_min = object.equivalent_min * min_rate

                amount_to_deduct += equivalent_min if object else 0.0

        else:
            wage = contract.get_wage(payslip_object, contract)

            amount_to_deduct += (((wage / contract.average_working_days) / 8.0) * late_hours)

        return amount_to_deduct
