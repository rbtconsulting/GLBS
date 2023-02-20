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


# class CheckFunctions(models.Model):
#      _inherit = 'hr.attendance'
#      @api.depends('employee_id', 'check_in', 'check_out',
#                  'work_time_line_id', 'is_absent',
#                  'overtime_id', 'overtime_id.rest_day_overtime',
#                  'overtime_id.start_time', 'overtime_id.end_time', 'leave_ids',
#                  'leave_ids.state', 'leave_ids.date_from', 'leave_ids.date_to',
#                  'overtime_id.state', 'request_change_id', 'request_change_id.state',
#                  'reg_holiday_ids.holiday_start', 'reg_holiday_ids.holiday_end',
#                  'reg_holiday_ids', 'reg_holiday_ids.holiday_type',
#                  'spl_holiday_ids.holiday_start', 'spl_holiday_ids.holiday_end',
#                  'spl_holiday_ids', 'spl_holiday_ids.holiday_type', 'rest_day_overtime',
#                  'is_holiday', 'is_leave', 'is_suspended')
#      def _worked_hours_computation(self):
#         for attendance in self:
#             TIME_TO_RENDER = attendance.work_time_line_id.time_to_render - attendance.work_time_line_id.break_period
#             night_shift = attendance.work_time_line_id.work_time_id.night_shift
#             ob_leaves = attendance.leave_ids.filtered(lambda l: l.holiday_status_id.is_ob)
#             leaves = attendance.leave_ids.filtered(lambda l: not l.holiday_status_id.is_ob)
#             """Get checkin/checkout time"""
#             # if (attendance.leave_ids and (ob_leaves or leaves) and not attendance.spl_holiday_ids and not attendance.reg_holiday_ids
#             #     and attendance.work_time_line_id and attendance.check_in and attendance.check_out):
#             #     for leave in ob_leaves:
#             #         ob_date_in = (context_timestamp(self, from_string(leave.date_from))).replace(second=0)
#             #         ob_date_out = (context_timestamp(self, from_string(leave.date_to))).replace(second=0)
#             #     ob_hours = attendance.get_ob_hours(ob_date_in, ob_date_out):

#             # for leave in leaves:
#             #     date_in = (context_timestamp(self, from_string(leave.date_from))).replace(second=0)
#             #     date_out = (context_timestamp(self, from_string(leave.date_to))).replace(second=0)
#             attendance.is_absent = False
#             if (not attendance.check_in or not attendance.check_out) and not ob_leaves:
#                 attendance.is_absent = True
#                 attendance.absent_hours = TIME_TO_RENDER
#                 return
#             if attendance.check_in and attendance.check_out:
#                 date_in = (context_timestamp(self, from_string(attendance.check_in))).replace(second=0)
#                 date_out = (context_timestamp(self, from_string(attendance.check_out))).replace(second=0)
#             if attendance.is_hide_check_time and ob_leaves:
#                 date_in = (context_timestamp(self, from_string(min(ob_leaves.mapped('date_from'))))).replace(second=0)
#                 date_out = (context_timestamp(self, from_string(max(ob_leaves.mapped('date_to'))))).replace(second=0)
#             """Required_in/required_out time"""
#             required_in_hour, required_in_minute = float_time_convert(attendance.work_time_line_id.latest_check_in)
#             required_in = date_in.replace(hour=required_in_hour, minute=required_in_minute, second=0)
#             leave_wp_hours = 0
#             leave_wop_hours = 0
#             ob_hours = 0
#             schedule_type = attendance.work_time_line_id.work_time_id.schedule_type
#             if schedule_type == 'coretime':
#                 if ob_leaves:
#                     ob_date_in = (context_timestamp(self, from_string(min(ob_leaves.mapped('date_from'))))).replace(second=0)
#                     if ob_date_in:
#                         date_in = min((context_timestamp(self, from_string(attendance.check_in))).replace(second=0), ob_date_in)
#                     else:
#                         date_in = (context_timestamp(self, from_string(attendance.check_in))).replace(second=0)
#                 earliest_in_hour, earliest_in_minute = float_time_convert(
#                     attendance.work_time_line_id.earliest_check_in)
#                 earliest_in = date_in.replace(hour=earliest_in_hour, minute=earliest_in_minute, second=0)

#                 latest_in_hour, latest_in_minute = float_time_convert(attendance.work_time_line_id.latest_check_in)
#                 latest_in = date_in.replace(hour=latest_in_hour, minute=latest_in_minute, second=0)

#                 if date_in < earliest_in:
#                     required_in = earliest_in
#                 if date_in >= earliest_in and date_in <= latest_in:
#                     required_in = date_in
#                 if date_in >= latest_in:
#                     required_in = latest_in
#             if attendance.reg_holiday_ids or attendance.spl_holiday_ids:
#                 holidays = attendance.reg_holiday_ids + attendance.spl_holiday_ids
#                 holiday_start = (context_timestamp(self, from_string(min(holidays.mapped('holiday_start'))))).replace(second=0)
#                 holiday_end = (context_timestamp(self, from_string(max(holidays.mapped('holiday_end'))))).replace(second=0)
#             else:
#                 holiday_start = False
#                 holiday_end = False

#             # check if night diff check in
#             required_in = get_intersection(date_in, date_out, required_in,
#                                            attendance.work_time_line_id.time_to_render)
#             required_out_hour, required_out_minute = float_time_convert(attendance.work_time_line_id.time_to_render)
#             required_out = required_in + timedelta(hours=required_out_hour, minutes=required_out_minute, seconds=0)
#             actual_time_in = date_in
#             actual_time_out = date_out

#             """Worked Hours with Lunch break"""
#             if attendance.work_time_line_id.break_period:
#                 break_period_hour, break_period_minute = float_time_convert(
#                     attendance.work_time_line_id.break_period)
#                 break_time = (break_period_hour + break_period_minute)
#                 lunch_break = required_in + timedelta(hours=4, minutes=0, seconds=0)
#                 lunch_break_period = lunch_break + timedelta(hours=break_period_hour, minutes=break_period_minute,
#                                                              seconds=0)
#                 worked_hours = 0
#                 if date_in < lunch_break:
#                     worked_hours += (min([date_out, lunch_break]) - max(
#                         [date_in, required_in])).total_seconds() / 3600.0
#                 if lunch_break_period < required_out and date_out > lunch_break_period:
#                     worked_hours += (min([date_out, required_out]) - max(
#                         [lunch_break_period, required_in])).total_seconds() / 3600.0
#                 if date_in > lunch_break_period and date_in < required_out:
#                     worked_hours = (min([date_out, required_out]) - max(
#                         [date_in, lunch_break_period])).total_seconds() / 3600.0
#                 if lunch_break <= date_in <= lunch_break_period:
#                     worked_hours = (min([date_out, required_out]) - max(
#                         [date_in, lunch_break_period])).total_seconds() / 3600.0
#                 if lunch_break <= date_in <= date_out <= lunch_break_period:
#                     worked_hours = 0
#             else:
#                 break_time = 0
#                 lunch_break = False
#                 lunch_break_period = False
#                 if holiday_start and holiday_end:
#                     if holiday_start >= date_in:
#                         in_date = max(date_in, required_in)
#                         out_date = min(date_out, holiday_start, required_out)
#                     else:
#                         in_date = max(holiday_end, date_in, required_in)
#                         out_date = min(date_out, required_out)
#                 else:
#                     in_date = max([date_in, required_in])
#                     out_date = min([date_out, required_out])
#                 worked_hours = (out_date - in_date).total_seconds() / 3600.0
#             if attendance.work_time_line_id:
#                 work_time = attendance.work_time_line_id.work_time_id
#             else:
#                 work_time = self.env['hr.employee.schedule.work_time'].search([
#                     ('employee_id', '=', attendance.employee_id.id), ('state', '=', 'approved')],
#                     order="priority", limit=1)
#             schedule_week_days = work_time.work_time_lines.mapped('days_of_week')
#             if attendance.check_in and attendance.check_out and attendance.work_time_line_id:
#                 """Worked Hours"""
#                 if worked_hours < 0.25:
#                     attendance.worked_hours = 0
#                 elif not attendance.is_hide_check_time and worked_hours > TIME_TO_RENDER:
#                     attendance.is_absent = False
#                     attendance.worked_hours = TIME_TO_RENDER
#                 elif not attendance.is_hide_check_time:
#                     attendance.is_absent = False
#                     attendance.worked_hours = worked_hours
#                 """OB Hours"""
#                 if attendance.leave_ids and ob_leaves and not attendance.reg_holiday_ids and not attendance.spl_holiday_ids:
#                     """OB hours if  no holiday"""
#                     for leave in ob_leaves:
#                         ob_date_in = (context_timestamp(self, from_string(leave.date_from))).replace(second=0)
#                         ob_date_out = (context_timestamp(self, from_string(leave.date_to))).replace(second=0)
#                     ob_hours = attendance.get_ob_hours(ob_date_in, ob_date_out, required_in, required_out,
#                                                        break_time, lunch_break, lunch_break_period)
#                     if required_in <= ob_date_in <= required_out:
#                         # attendance.worked_hours = 0
#                         attendance.ob_hours = ob_hours
#                         attendance.is_absent = False
#                     if ob_hours < 0.25:
#                         attendance.ob_hours = 0
#                     elif ob_hours > TIME_TO_RENDER:
#                         attendance.is_absent = False
#                         attendance.ob_hours = TIME_TO_RENDER
#                         ob_hours = TIME_TO_RENDER
#                     else:
#                         attendance.is_absent = False
#                         attendance.ob_hours = ob_hours
#                 """OB hours if holiday (night shift)"""
#                 if (attendance.reg_holiday_ids or attendance.spl_holiday_ids) and night_shift:
#                     if attendance.leave_ids and ob_leaves:
#                         leave_date_in = []
#                         leave_date_out = []
#                         for leave in ob_leaves:
#                             leave_date_in.append(context_timestamp(self, from_string(leave.date_from)))
#                             leave_date_out.append(context_timestamp(self, from_string(leave.date_to)))
#                         date_in = min(leave_date_in)
#                         date_out = max(leave_date_out)
#                     if attendance.reg_holiday_ids or attendance.spl_holiday_ids:
#                         """With lunch break"""
#                         if attendance.work_time_line_id.break_period:
#                             hours = 0
#                             if date_in < lunch_break:
#                                 hours += (min([date_out, lunch_break, holiday_end]) - max(
#                                     [date_in, required_in])).total_seconds() / 3600.0
#                             if lunch_break_period < required_out and date_out > lunch_break_period:
#                                 hours += (min([holiday_end, required_out, date_out]) - max(
#                                     [lunch_break_period, required_in, holiday_start, date_in])).total_seconds() / 3600.0
#                             if holiday_end < date_out:
#                                 if date_in < lunch_break:
#                                     hours = 0
#                                     hours += (min([date_out, lunch_break]) - max(
#                                         [date_in, required_in, holiday_end])).total_seconds() / 3600.0
#                                 if lunch_break_period < required_out and date_out > lunch_break_period:
#                                     hours += (min([required_out, date_out]) - max(
#                                         [lunch_break_period, date_in])).total_seconds() / 3600.0
#                             if holiday_end > date_out:
#                                 hours = (min([date_out, lunch_break, holiday_start]) - max(
#                                     [date_in, required_in])).total_seconds() / 3600.0
#                             if date_in > lunch_break_period and date_in < required_out:
#                                 hours = (min([date_out, required_out]) - max(
#                                     [date_in, lunch_break_period])).total_seconds() / 3600.0
#                             if lunch_break <= date_in <= lunch_break_period:
#                                 hours = (min([date_out, required_out]) - max(
#                                     [date_in, lunch_break_period])).total_seconds() / 3600.0
#                             if date_in > holiday_start and holiday_end > date_out:
#                                 hours = 0
#                             if lunch_break <= date_in <= date_out <= lunch_break_period:
#                                 hours = 0
#                         else:
#                             break_time = 0
#                             lunch_break = False
#                             lunch_break_period = False
#                             if holiday_start >= date_in:
#                                 in_date = max(date_in, required_in)
#                                 out_date = min(date_out, holiday_start, required_out)
#                             else:
#                                 in_date = max(holiday_end, date_in, required_in)
#                                 out_date = min(date_out, required_out)
#                             hours = (out_date - in_date).total_seconds() / 3600.0
#                         if attendance.leave_ids and ob_leaves:
#                             attendance.ob_hours = hours or 0
#                             ob_hours = hours
#                         else:
#                             attendance.worked_hours = hours or 0
#                     # elif attendance.reg_holiday_ids or attendance.spl_holiday_ids:
#                     #     attendance.worked_hours = 0
#                 """Leave Hours"""
#                 if attendance.leave_ids and leaves:
#                     ob_hours = attendance.ob_hours
#                     worked_leave_hours = 0
#                     for leave in leaves:
#                         leave_hours = attendance.calculate_leave_hours(leave, lunch_break, lunch_break_period,
#                                                                        date_in, date_out, required_in, required_out, worked_leave_hours)
#                         leave_wp_hours += leave_hours['leave_wp_hours']
#                         leave_wop_hours += leave_hours['leave_wop_hours']
#                         worked_leave_hours = leave_hours['worked_hours']
#                     attendance.leave_hours = leave_wp_hours > 0 and leave_wp_hours or 0
#                     attendance.leave_wop_hours = leave_wop_hours > 0 and leave_wop_hours or 0
#                     if not attendance.is_absent and not attendance.is_holiday and not attendance.is_leave and not attendance.is_ob:
#                         hours = worked_leave_hours - ob_hours
#                         attendance.worked_hours = hours > 0 and hours or 0
#                         attendance.absent_hours = 0
#             """Overtime Calculation"""
#             min_overtime_hours = float(self.env['ir.config_parameter'].get_param('minimum.overtime.hours', '1'))
#             if attendance.overtime_id and attendance.overtime_id.state == 'approved':
#                 date_in = (context_timestamp(self, from_string(attendance.check_in))).replace(second=0)
#                 date_out = (context_timestamp(self, from_string(attendance.check_out))).replace(second=0)
#                 if attendance.leave_ids and ob_leaves:
#                     for leave in ob_leaves:
#                         ob_date_in = (context_timestamp(self, from_string(leave.date_from))).replace(second=0)
#                         ob_date_out = (context_timestamp(self, from_string(leave.date_to))).replace(second=0)

#                         date_in = min([date_in, ob_date_in]) or date_in
#                         date_out = max([date_out, ob_date_out]) or date_out

#                 overtime_start_time = (context_timestamp(self, from_string(attendance.overtime_id.start_time))).replace(second=0)
#                 overtime_end_time = (context_timestamp(self, from_string(attendance.overtime_id.end_time))).replace(second=0)
#                 min_end = min([date_out, overtime_end_time])
#                 max_start = max([date_in, overtime_start_time])
#                 overtime = (min_end - max_start).total_seconds() / 3600.0
#                 """Regular Ot"""
#                 if overtime > min_overtime_hours:
#                     #                     if attendance.work_time_line_id:
#                     #                         work_time = attendance.work_time_line_id.work_time_id
#                     #                     else:
#                     #                         work_time = self.env['hr.employee.schedule.work_time'].search([(
#                     #                             'employee_id', '=', attendance.employee_id.id),('state', '=', 'approved')], order="priority", limit=1)
#                     #                     schedule_week_days = work_time.work_time_lines.mapped('days_of_week')
#                     restday_overtime_after = 0
#                     restday_overtime_before = 0
#                     restday_overtime = 0
#                     midnight = min_end.replace(hour=0, minute=0)
#                     if not overtime_end_time.strftime('%A').lower() in schedule_week_days and attendance.work_time_line_id:
#                         restday_overtime_after = (min_end - max([required_out, midnight])).total_seconds() / 3600.0
#                         overtime_hours = (midnight - max_start).total_seconds() / 3600.0
#                     elif not attendance.work_time_line_id:
#                         restday_overtime_before = overtime
#                     # if not overtime_start_time.strftime('%A').lower() in schedule_week_days:
#                     #     restday_overtime_before = (midnight - max_start).total_seconds() / 3600.0
#                     #     overtime_hours = (min_end - midnight).total_seconds() / 3600.0
#                     if attendance.overtime_id.with_break:
#                         ot_break_period = attendance.overtime_id.break_period + attendance.overtime_id.break_period2
#                         overtime -= ot_break_period
#                     if holiday_start and holiday_end and overtime_start_time > holiday_start and overtime_start_time < holiday_end:
#                         overtime_hours = 0
#                     else:
#                         overtime_hours = overtime
#                     restday_overtime = restday_overtime_after + restday_overtime_before
#                     if restday_overtime and attendance.overtime_id.with_break:
#                         # overtime_hours = overtime_hours - break_time
#                         restday_overtime = restday_overtime - ot_break_period
#                     if restday_overtime > HOURS_PER_DAY:
#                         attendance.rest_day_hours = HOURS_PER_DAY
#                         attendance.rest_day_ot_hours = restday_overtime - HOURS_PER_DAY
#                     else:
#                         attendance.rest_day_hours = restday_overtime > 0 and restday_overtime or 0
#                     if attendance.work_time_line_id and not (attendance.reg_holiday_ids or attendance.spl_holiday_ids):
#                         if overtime_hours and restday_overtime and overtime_hours > restday_overtime:
#                             overtime_hours = overtime_hours - restday_overtime
#                         attendance.overtime_hours = overtime_hours > 0 and overtime_hours or 0
#                     else:
#                         if attendance.leave_ids and ob_leaves:
#                             actual_rest_day_overtime_rendered_hours = attendance.calculate_overtime_fields_with_ob()
#                             # overtime = actual_rest_day_overtime_rendered_hours
#                         # if overtime > TIME_TO_RENDER:
#                         #     holiday_working_hours = TIME_TO_RENDER
#                         #     holiday_ot_working_hours = overtime - TIME_TO_RENDER
#                         # else:
#                         #     holiday_working_hours = overtime > 0 and overtime or 0
# #                         if not attendance.work_time_line_id:
# #                             attendance.rest_day_hours = holiday_working_hours
# #                             attendance.rest_day_ot_hours = holiday_ot_working_hours
# #                         if attendance.work_time_line_id:

#                         if attendance.spl_holiday_ids or attendance.reg_holiday_ids:
#                             reg_holiday_hours = 0
#                             spl_holiday_hours = 0
#                             holiday_hours = attendance.calculate_holiday_hours()
#                             reg_holiday_hours += holiday_hours['regular_holiday_hours']
#                             spl_holiday_hours += holiday_hours['special_holiday_hours']
#                             if reg_holiday_hours > HOURS_PER_DAY:
#                                 reg_holiday_working_hours = HOURS_PER_DAY
#                                 reg_holiday_ot_working_hours = reg_holiday_hours - HOURS_PER_DAY
#                             else:
#                                 reg_holiday_working_hours = reg_holiday_hours > 0 and reg_holiday_hours or 0
#                                 reg_holiday_ot_working_hours = 0

#                             if spl_holiday_hours > HOURS_PER_DAY:
#                                 spl_holiday_working_hours = HOURS_PER_DAY
#                                 spl_holiday_ot_working_hours = spl_holiday_hours - HOURS_PER_DAY
#                             else:
#                                 spl_holiday_working_hours = spl_holiday_hours > 0 and spl_holiday_hours or 0
#                                 spl_holiday_ot_working_hours = 0

#                             attendance.is_holiday = True
#                             attendance.sp_holiday_hours = attendance.spl_holiday_ids and spl_holiday_working_hours or 0
#                             attendance.sp_hday_ot_hours = attendance.spl_holiday_ids and spl_holiday_ot_working_hours or 0
#                             attendance.reg_holiday_hours = attendance.reg_holiday_ids and reg_holiday_working_hours or 0
#                             attendance.reg_hday_ot_hours = attendance.reg_holiday_ids and reg_holiday_ot_working_hours or 0
#                             # calculate overtime again with considering the holiday
#                             if attendance.work_time_line_id:
#                                 if overtime_start_time >= holiday_end or overtime_end_time <= holiday_start:
#                                     attendance.overtime_hours = overtime_hours > 0 and overtime_hours or 0
#                                 elif overtime_hours and not night_shift and holiday_start.date() != date_in.date():
#                                     attendance.overtime_hours = overtime_hours > 0 and overtime_hours or 0
#                                 elif overtime_hours and (reg_holiday_hours or spl_holiday_hours) and overtime_hours > (reg_holiday_hours + spl_holiday_hours):
#                                     attendance.overtime_hours = overtime_hours - (reg_holiday_hours + spl_holiday_hours)
#                 else:
#                     attendance.overtime_hours = 0
#                     if attendance.reg_holiday_ids or attendance.spl_holiday_ids:
#                         attendance.is_holiday = True
#             if attendance.work_time_line_id and not ob_leaves and not ((actual_time_out - actual_time_in).total_seconds() / 3600.0) > 1:
#                 if holiday_end and holiday_start:
#                     actual_holiday_hours = (min(holiday_end, required_out) - max(holiday_start, required_in)).total_seconds() / 3600.0
#                     attendance.absent_hours = (TIME_TO_RENDER - actual_holiday_hours) > 0 and (TIME_TO_RENDER - actual_holiday_hours) or 0
#                 else:
#                     attendance.is_absent = True
#                     attendance.absent_hours = TIME_TO_RENDER
#             else:
#                 attendance.is_absent = False
#             if attendance.is_absent or attendance.is_suspended or actual_time_out <= required_in or actual_time_in >= required_out:
#                 attendance.worked_hours = 0
#             if not attendance.work_time_line_id or (not night_shift and attendance.is_holiday):
#                 attendance.overtime_hours = attendance.overtime_hours > 0 and attendance.overtime_hours or 0
#                 attendance.is_absent = False
#                 attendance.absent_hours = 0
#                 attendance.ob_hours = 0
#             if holiday_end and holiday_start and required_in >= holiday_start and required_out <= holiday_end:
#                 attendance.worked_hours = 0
#             if attendance.work_time_line_id and leaves and not ob_leaves and not attendance.is_holiday and not attendance.worked_hours:
#                 attendance.is_absent = True
#                 attendance.absent_hours = TIME_TO_RENDER - attendance.leave_hours - attendance.leave_wop_hours
#             if (leave_wp_hours + leave_wop_hours + ob_hours + attendance.late_hours + attendance.undertime_hours) >= TIME_TO_RENDER:
#                 attendance.worked_hours = 0
#             """if holidays(Holiday Settings)"""
#             if attendance.check_in and attendance.check_out and schedule_week_days and (attendance.reg_holiday_ids or attendance.spl_holiday_ids):
#                 attendance.absent_hours = attendance._validate_holidays(schedule_week_days)
