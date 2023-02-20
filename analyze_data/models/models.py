# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError

class AnalyzeData(models.Model):
    _inherit = 'hr.payslip'

    attendance_data = fields.Many2many('hr.attendance')
    def get_worked_hour_lines(self, employee_id, date_from, date_to):

        x =  super(AnalyzeData, self).get_worked_hour_lines(employee_id, date_from, date_to)
        # raise ValidationError(x)
        self.attendance_data = [(4, i.id, None) for i in x]
        return x