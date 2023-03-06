from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


def convert_time_to_float(time):
    hours = time.seconds // 3600
    minutes = (time.seconds // 60) % 60
    total_hrs = float(minutes) / 60 + hours
    return total_hrs


def checking_holiday_setting(holiday_date_data):
    holiday_type = []
    for holiday_type_setting in holiday_date_data:
        if holiday_type_setting.holiday_type == 'regular' and holiday_type_setting.before == True:
            holiday_type.append(1)
        if holiday_type_setting.holiday_type == 'regular' and holiday_type_setting.before == False:
            holiday_type.append(2)
        if holiday_type_setting.holiday_type == 'special' and holiday_type_setting.before == True:
            holiday_type.append(3)
        if holiday_type_setting.holiday_type == 'special' and holiday_type_setting.before == False:
            holiday_type.append(4)

    return holiday_type


def intersection_list(list1, list2):
    return list(set(list1) & set(list2))


class LeavesAutomate(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def action_approve(self):
        # raise ValidationError(self.id)

        if self.date_from and self.date_to:
            y = self.env['hr.attendance'].create({
                'employee_id': self.employee_id.id,
                'check_in': self.date_from,
                'check_out': self.date_to,
            })

            y.write({'leave_ids': [(4, self.id)]})

        x = super(LeavesAutomate, self).action_approve()
        return x


class AdditionalTables(models.Model):
    _inherit = 'payroll.sss.contribution'

    wsip_er = fields.Float(string="WSIP ER")
    wsip_ee = fields.Float(string="WSIP EE")


class SalaryRulesAdditional(models.Model):
    _inherit = 'hr.contract'

    def get_prev_regwrk(self, contract, payslip):
        domain = [('date_release', '<', payslip.date_release), ('contract_id', '=', contract.id), ('contract_id.employee_id', '=', contract.employee_id.id)]
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

    def get_prev_gross(self, contract, payslip):
        domain = [('date_release', '<', payslip.date_release), ('contract_id', '=', contract.id), ('contract_id.employee_id', '=', contract.employee_id.id)]
        prev_payslip = self.env['hr.payslip'].search(domain, limit=1, order="date_release DESC")
        if prev_payslip:
            datas = {'GTP': 0.0}
            for line in prev_payslip.line_ids:
                if line.category_id.code in datas:
                    datas[line.category_id.code] += line.total
                else:
                    continue
            total_prev_regwrk = datas['GTP']
            if total_prev_regwrk:
                return total_prev_regwrk
        return 0.0

    def meal_allowance_revised(self, contract, date_from, date_to):
        date_from_converted = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_converted = datetime.strptime(date_to, '%Y-%m-%d').date()
        get_attendance = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id['id']), ('check_in', '>=', str(date_from_converted)),
                                                           ('check_in', '<=', str(date_to_converted))])
        get_holidays = self.env['hr.attendance.holidays'].search([])
        worked_days = 0

        for date_attendance in get_attendance:
            if date_attendance.worked_hours > 0.0000000001:
                worked_days += 1

        return worked_days

    def get_holiday_days(self, contract, payslip):
        date_from_converted = datetime.strptime(payslip.date_from, '%Y-%m-%d').date()
        date_to_converted = datetime.strptime(payslip.date_to, '%Y-%m-%d').date()
        get_attendance = self.env['hr.attendance'].search([('employee_id', '=', contract.employee_id['id']), ('check_in', '>=', str(date_from_converted)),
                                                           ('check_in', '<=', str(date_to_converted))])
        get_holidays = self.env['hr.attendance.holidays'].search([])
        get_holiday_setting = self.env['hr.holiday.setting'].search([])
        get_days_holiday = []
        get_day_reg = []
        call_holiday_setting = checking_holiday_setting(get_holiday_setting)
        for day_attendance in get_attendance:
            if day_attendance.worked_hours > 0.001:
                get_day_reg.append(datetime.strptime(day_attendance.check_in, '%Y-%m-%d %H:%M:%S').date())

        for holiday_setting in call_holiday_setting:
            for holiday_date in get_holidays:
                if holiday_setting == 1:
                    if datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() >= date_from_converted and datetime.strptime(
                            holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() <= date_to_converted and holiday_date.holiday_type == 'regular':
                        get_add = datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() + timedelta(days=1)
                        get_days_holiday.append(get_add)
                elif holiday_setting == 2:
                    if datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() >= date_from_converted and datetime.strptime(
                            holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() <= date_to_converted and holiday_date.holiday_type == 'regular':
                        get_add = datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date()
                        get_days_holiday.append(get_add)
                elif holiday_setting == 3:
                    if datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() >= date_from_converted and datetime.strptime(
                            holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() <= date_to_converted and holiday_date.holiday_type == 'special':
                        get_add = datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() + timedelta(days=1)
                        get_days_holiday.append(get_add)
                elif holiday_setting == 4:
                    if datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() >= date_from_converted and datetime.strptime(
                            holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() <= date_to_converted and holiday_date.holiday_type == 'special':
                        get_add = datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date()
                        get_days_holiday.append(get_add)
                else:
                    if datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() >= date_from_converted and datetime.strptime(
                            holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() <= date_to_converted and holiday_date.holiday_type == 'regular':
                        get_add = datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date()
                    if datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() >= date_from_converted and datetime.strptime(
                            holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date() <= date_to_converted and holiday_date.holiday_type == 'special':
                        get_add = datetime.strptime(holiday_date.holiday_start, '%Y-%m-%d  %H:%M:%S').date()
                        get_days_holiday.append(get_add)

        get_intersection = intersection_list(get_day_reg, get_days_holiday)

        holiday_payment_no_attendance = 0

        for n in get_days_holiday:
            if n not in get_intersection:
                holiday_payment_no_attendance += 1

        return holiday_payment_no_attendance


# test model for salary rules
# class TestModel(models.Model):
#     _inherit = 'hr.payslip'