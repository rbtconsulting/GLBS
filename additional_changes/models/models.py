from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import ValidationError,UserError
from odoo.tools.translate import _
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta


def convert_time_to_float(time):
    hours = time.seconds // 3600
    minutes = (time.seconds // 60) % 60
    total_hrs = float(minutes) / 60 + hours
    return total_hrs
class GetEmployees(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def action_approve(self):
        # raise ValidationError(self.id)
        y = self.env['hr.attendance'].create({
            'employee_id' : self.employee_id.id,
            'check_in' : self.date_from,
            'check_out': self.date_to,
        })
    
        y.write({'leave_ids': [(4, self.id)]})

        x =  super(GetEmployees, self).action_approve()
        return x

class AdditionalTables(models.Model):
    _inherit = 'payroll.sss.contribution'

    wsip_er = fields.Float(string="WSIP ER")
    wsip_ee = fields.Float(string="WSIP EE")


class PhicAdditional(models.Model):    
    _inherit = 'hr.contract'

    def get_prev_regwrk(self, contract, payslip):
        domain = [('date_release', '<', payslip.date_release),
                    ('contract_id', '=', contract.id),
                    ('contract_id.employee_id', '=', contract.employee_id.id)]
        prev_payslip = self.env['hr.payslip'].search(domain, limit=1, order="date_release DESC")
        if prev_payslip:
            datas = {'RegWrk': 0.0}
            for line in prev_payslip.line_ids:
                if line.code in datas:
                    datas[line.code] += line.total
                else:
                    continue
            total_prev_regwrk = datas['RegWrk']
            if total_prev_regwrk:
                return total_prev_regwrk
        return 0.0

# class MealAllowance(models.Model):
#     _inherit = 'hr.payslip'

#     @api.multi
#     def meal_allowance_revised(self):
#     #    get_payslip_test = self.contract_id
#         # check_out = datetime.strptime(n.check_out, '%Y-%m-%d %H:%M:%S')
#         # date_from = self.payroll_period_id.start_date
#         # date_to = self.payroll_period_id.end_date
#         # date_from_converted = datetime.strptime(date_from, '%Y-%m-%d').date()
#         # date_to_converted = datetime.strptime(date_to, '%Y-%m-%d').date()
#         # get_attendance = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id['id']),('check_in', '>=',str(date_from_converted)),('check_in','<=', str(date_to_converted))])
#         # worked_days = 0

#         # for date_attendance in get_attendance:
#         #     if date_attendance.worked_hours > 0.0000000001:
#         #         worked_days += 1

#         return 1.0
    

class MealAllowance(models.Model):
    _inherit = 'hr.contract'
    
    def meal_allowance_revised(self, contract, date_from, date_to):
        date_from_converted = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_converted = datetime.strptime(date_to, '%Y-%m-%d').date()
        get_attendance = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id['id']),('check_in', '>=',str(date_from_converted)),('check_in','<=', str(date_to_converted))])
        worked_days = 0

        for date_attendance in get_attendance:
            if date_attendance.worked_hours > 0.0000000001:
                worked_days += 1

        return worked_days

