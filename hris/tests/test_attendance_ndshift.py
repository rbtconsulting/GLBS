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
           
    def test_attendance1(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-06 22:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 07:00:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
          
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
         
        self.assertEqual(attendance.worked_hours, 8, 'Worked hours must be 8!')
        self.assertEqual(attendance.night_diff_hours, 7, 'Night Shift Differential must be equal to 7!')
        self.assertEqual(attendance.undertime_hours, 0, 'Undertime hours must be zero!')
        self.assertEqual(attendance.late_hours, 0, 'Late hours must be zero!')
        
    def test_attendance2(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-06 23:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 06:00:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
          
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
         
        self.assertEqual(attendance.worked_hours, 6, 'Worked hours must be 6!')
        self.assertEqual(attendance.night_diff_hours, 6, 'Night Shift Differential must be equal to 6!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime hours must be 1!')
        self.assertEqual(attendance.late_hours, 1, 'Late hours must be 1!')
        
    def test_attendance3(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 01:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 06:00:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
          
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
         
        self.assertEqual(attendance.worked_hours, 4, 'Worked hours must be 4!')
        self.assertEqual(attendance.night_diff_hours, 4, 'Night Shift Differential must be equal to 4!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime hours must be zero!')
        self.assertEqual(attendance.late_hours, 3, 'Late hours must be 3!')
    
    def test_attendance4(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-06 08:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 06:00:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
          
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
         
        self.assertEqual(attendance.worked_hours, 7, 'Worked hours must be 7!')
        self.assertEqual(attendance.night_diff_hours, 7, 'Night Shift Differential must be equal to 7!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime hours must be 1!')
        self.assertEqual(attendance.late_hours, 0, 'Late hours must be 0!')
    
    def test_attendance5(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 01:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 06:00:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-06 22:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 01:00:00'), self.env.user.tz))
        
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
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
         
        self.assertEqual(attendance.worked_hours, 4, 'Worked hours must be 4!')
        self.assertEqual(attendance.leave_hours, 3, 'Leave hours must be 3!')
        self.assertEqual(attendance.night_diff_hours, 4, 'Night Shift Differential must be equal to 4!')
        self.assertEqual(attendance.undertime_hours, 1, 'Undertime hours must be 1!')
        self.assertEqual(attendance.late_hours, 0, 'Late hours must be 0!')
    
    def test_attendance6(self):
        self.check_in = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 02:00:00'), self.env.user.tz))
        self.check_out = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 06:00:00'), self.env.user.tz))
        
        #create attendance
        self.employee_id = self.env['hr.employee'].search([('barcode', '=', '2017-0010')]).id
    
        self.attendance = self.env['hr.attendance'].create({
                                    'employee_id': self.employee_id,
                                    'check_in': self.check_in,
                                    'check_out': self.check_out
                                    })
        # I Will file a half day leaves
        date_from = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-06 22:00:00'), self.env.user.tz))
        date_to = fields.Datetime.to_string(context_utc(fields.Datetime.from_string('2018-07-07 01:00:00'), self.env.user.tz))
        
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
        
        attendance = self.attendance
        
        self.assert_(self.attendance, 'Attendance has not been created!')
         
        self.assertEqual(attendance.worked_hours, 3, 'Worked hours must be 3!')
        self.assertEqual(attendance.leave_hours, 3, 'Leave hours must be 3!')
        self.assertEqual(attendance.night_diff_hours, 3, 'Night Shift Differential must be equal to 3!')
        self.assertEqual(attendance.undertime_hours, 2, 'Undertime hours must be 2!')
        self.assertEqual(attendance.late_hours, 0, 'Late hours must be 0!')
                