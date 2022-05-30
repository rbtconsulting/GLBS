from odoo.tests import common
from odoo import fields
import pytz

def context_utc(date, timezone):
    """Returns date and time into utc format."""
    if not date:
        return ''

    if not timezone:
        timezone = 'UTC'

    tz = pytz.timezone(timezone)
    local_date = tz.localize(date, is_dst=None)
    utc_date = local_date.astimezone(pytz.utc)

    return utc_date

class TestAttendance(common.TransactionCase):
    
    def setUp(self):
        super(TestAttendance, self).setUp()
           
    def test_attendance_with_full_leaves(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 08:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 17:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 08:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 0, 'Worked hours must be zero!')
        self.assertEqual(attendance.leave_hours, 8, 'Leave with pay must be equal to 8!')
        self.assertEqual(attendance.leave_wop_hours, 0, 'Leave without pay must be zero!')
        
    def test_attendance_with_leaves_on_range(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 08:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 17:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 08:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-22 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 0, 'Worked hours must be zero!')
        self.assertEqual(attendance.leave_hours, 8, 'Leave with pay must be equal to 8!')
        self.assertEqual(attendance.leave_wop_hours, 0, 'Leave without pay must be equal zero!')
    
    def test_attendance_between_with_leaves_on_range(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 08:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-20 08:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-22 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 0, 'Worked hours must be zero!')
        self.assertEqual(attendance.leave_hours, 8, 'Leave with pay must be equal to 8!')
        self.assertEqual(attendance.leave_wop_hours, 0, 'Leave without pay must be equal to zero!')
    
    def test_attendance_with_second_fourhour_leaves(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 08:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 12:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 13:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 4, 'Worked hours must be equal to 4!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.leave_wop_hours, 0, 'Leave without pay must be equal to zero!')
    
    def test_attendance_with_first_fourhour_leaves(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 13:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 8:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 12:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 4, 'Worked hours must be equal to 4!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.leave_wop_hours, 0, 'Leave without pay must be equal to zero!')
    
    def test_attendance_between_second_fourhour_leaves_with_ut(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 08:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 11:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 13:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 3, 'Worked hours must be equal to 3!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.leave_wop_hours, 0, 'Leave without pay must be equal to zero!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime must be equal to 1!')
    
    def test_attendance_between_second_fourhour_leaves_with_late(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 09:30:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 11:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 13:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 2, 'Worked hours must be equal to 3!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.late_hours, 1, 'Late must be equal to 1!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime must be equal to 1!')
    
    
    def test_attendance_between_second_fourhour_leaves_with_b4in(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 07:30:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 07:35:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 13:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 0, 'Worked hours must be equal to 0!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.late_hours, 0, 'Late must be equal to 0!')
        self.assertEqual(attendance.undertime_hours, 0, 'Undertime must be equal to 0!')
        self.assertEqual(attendance.absent_hours, 4, 'Absent must be equal to 0!')
        
    def test_attendance_between_second_fourhour_leaves_with_after_out(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 15:30:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 13:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 0, 'Worked hours must be equal to 0!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.late_hours, 4, 'Late must be equal to 4!')
        self.assertEqual(attendance.undertime_hours, 0, 'Undertime must be equal to 0!')
        self.assertEqual(attendance.absent_hours, 0, 'Absent must be equal to 0!')
    
    def test_attendance_between_second_fourhour_leaves_with_after_lunchperiod(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 14:30:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 17:35:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 08:30:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-06-21 12:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 3, 'Worked hours must be equal to 3!')
        self.assertEqual(attendance.leave_hours, 4, 'Leave with pay must be equal to 4!')
        self.assertEqual(attendance.late_hours, 0, 'Late must be equal to 1!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime must be equal to 0!')
        self.assertEqual(attendance.absent_hours, 0, 'Absent must be equal to 0!')
    
    def test_attendance_between_second_fourhour_leaves_with_after_lunchperiod2_without_intersection(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-15 7:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-15 14:30:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-15 15:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-15 17:30:00'), self.env.user.tz))
        
        self.holidays = self.env['hr.holidays'].create({
                                            'employee_id': self.employee_id,
                                            'holiday_status_id': self.env['hr.holidays.status'].search([('limit', '=', True)], limit=1).id,
                                            'holiday_type': 'employee',
                                            'date_from': date_from,
                                            'date_to': date_to,
                                            'type': 'remove',
                                            })
        #Approve the leave
        self.holidays.action_approve()
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
        self.assertEqual(attendance.leave_ids.ids,self.holidays.ids, 'Leaves on attendance is not equal')
        
        self.assertEqual(attendance.worked_hours, 5, 'Worked hours must be equal to 5.0!')
        self.assertEqual(attendance.leave_hours, 2.5, 'Leave with pay must be equal to 2.50!')
        self.assertEqual(attendance.late_hours, 0, 'Late must be equal to 0!')
        self.assertEqual(attendance.undertime_hours, 0.50, 'Undertime must be equal to 0.50!')
        self.assertEqual(attendance.absent_hours, 0, 'Absent must be equal to 0!')        