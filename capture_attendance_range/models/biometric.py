

from odoo import models, api,fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz, logging

_logger = logging.getLogger(__name__)

class Biometric(models.Model):
    _inherit = 'hr.biometric.connection'

    def rec_to_utc(self, to_convert):
        tz_name = self._context.get('tz') or self.env.user.tz

        local = pytz.timezone('Asia/Manila')
        local_dt_log = local.localize(to_convert, is_dst=None)
        return local_dt_log.astimezone(pytz.utc)

    def get_employee_logs(self, barcode, from_dt, night_shift):
        if night_shift:
            from_date = datetime.combine(from_dt, datetime.min.time()).replace(hour=12, minute=0)
            to_date = datetime.combine(from_dt, datetime.min.time()) + relativedelta(days=1, hour=12)
            where_clause = """ and (bio_timestamp AT TIME ZONE 'UTC' AT TIME ZONE '%s')>='%s'
                and (bio_timestamp AT TIME ZONE 'UTC' AT TIME ZONE '%s') <= '%s'
            """ % (
                self._context.get('tz', 'Asia/Manila'), from_date,
                self._context.get('tz', 'Asia/Manila'), to_date)
        else:
            where_clause = " and to_char(bio_timestamp AT TIME ZONE 'UTC' AT TIME ZONE '%s','yyyy-mm-dd')='%s'" % (
                self._context.get('tz', 'Asia/Manila'), from_dt.strftime(DEFAULT_SERVER_DATE_FORMAT))

        self._cr.execute("""
            select id from hr_biometric_log
            where user_id='%s' %s
            and log_processed='f' order by bio_timestamp
        """ % (str(barcode), where_clause))
        emp_logs = [emp[0] for emp in self._cr.fetchall()]
        return emp_logs

    @api.multi
    def action_process_attendance_cron(self,from_dt, night_shift=False):
        attendances_list = []
        # if self.branch_id:
        #     domain += [('branch_id', '=', self.branch_id.id)]
        logs = []
        work_time_schedule = self.env['hr.employee.schedule.work_time']
        shift_schedule = work_time_schedule.search([('night_shift', '=', night_shift)])
        for employee in shift_schedule.filtered(lambda l: l.employee_id.state not in ['relieved', 'terminate']).mapped('employee_id'):
            if not employee.barcode:
                _logger.info('Employee %s has no barcode.' % (employee.name))

                continue
            if not employee.barcode.isdigit():
                _logger.info('Employee %s barcode must be integer.' % (employee.name))
                continue

            emp_logs = self.get_employee_logs(employee.barcode, from_dt, night_shift)
            attendance_record = {}
            emp_logs = self.env['hr.biometric.log'].browse(emp_logs)
            logs += emp_logs
            for record in emp_logs:
                local_timestamp = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                    record.bio_timestamp))
                _logger.info("MMM::::%s::::%s" %(record.bio_timestamp, local_timestamp))
                date_log = local_timestamp.strftime('%Y-%m-%d')
                time_log = local_timestamp.strftime('%H:%M:%S')
                key = employee.barcode, date_log

                if key in attendance_record:
                    attendance_record[key].append(record)
                else:
                    attendance_record[key] = [record]
            if not attendance_record:
                _logger.info('Employee %s has no attendances.' % (employee.name))
                continue
            list_time = []
            is_absent = False
            for key, timestamp in sorted(attendance_record.items(), key=lambda r: r[1]):
                for time in timestamp:
                    list_time.append(time.bio_timestamp)
                if not list_time:
                    list_time = [utc_dt_to.strftime('%Y-%m-%d %H:%M:%S')]
                    is_absent = True
                if len(list_time) == 0:
                    is_absent = True
                if len(list_time) == 1:
                    is_absent = True
            list_time_in = min(list_time)
            list_time_out = max(list_time)
            if list_time_in == list_time_out:
                is_absent = True
            attendances_list.append((employee, list_time_in, list_time_out, is_absent))
            _logger.info('Processing the attendances.%s' % (employee.name))
        return logs, dict(attendance=attendances_list, from_utc=from_dt.strftime(DEFAULT_SERVER_DATE_FORMAT) + " 00:00:00", to_utc=from_dt.strftime(DEFAULT_SERVER_DATE_FORMAT) + " 23:59:59")

    @api.model
    def action_absent_employee_attendance_cron(self, date, night_shift=False):
        schedule_work_time_ids = self.env['hr.employee.schedule.work_time'].search([
                            ('state', '=', 'approved'), ('start_date', '<=', date.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                            ('end_date', '>=', date.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                            ('night_shift', '=', night_shift),
                            ('work_time_lines.days_of_week', '=', date.strftime("%A").lower())])
        employee_ids = schedule_work_time_ids.filtered(lambda l: l.employee_id.state not in ['relieved', 'terminate']).mapped('employee_id')
        self._cr.execute("""
            select user_id from hr_biometric_log
            where to_char(bio_timestamp AT TIME ZONE 'UTC' AT TIME ZONE '%s','yyyy-mm-dd')='%s'
        """ % (self._context.get('tz', 'Asia/Manila'), date.strftime(DEFAULT_SERVER_DATE_FORMAT)))
        emp_logs = [emp[0] for emp in self._cr.fetchall()]
        absent_employee_ids = employee_ids.filtered(lambda e: e.employee_code not in emp_logs)
        values = {
            'is_raw': True,
            'is_absent': True,
            'remarks': 'ABS',
        }
        attendance_obj = self.env['hr.attendance']
        for employee in absent_employee_ids:
            values.update({
                'employee_id': employee.id,
                'work_time_line_id': schedule_work_time_ids.filtered(
                    lambda w: w.employee_id == employee).work_time_lines.filtered(
                    lambda l: l.days_of_week == date.strftime("%A").lower())[0].id
            })
            same_attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', employee.id), ('schedule_in', '>=', fields.Date.to_string(date)),
                 ('schedule_in', '<=', fields.Date.to_string(date + timedelta(days=+1)))])
            if not same_attendance:
                try:
                    attendance_id = attendance_obj.with_context(default_cron_schedule_time=date).create(values)
                    attendance_id.with_context(update_from_cron=True).write({'check_in': attendance_id.schedule_in, 'check_out': attendance_id.schedule_in})
                    _logger.info("Creating absent attendance logs of employee %s with %s " % (
                        employee.name, attendance_id.schedule_in))
                except Exception as e:
                    _logger.info('Can not create attendance log of employee %s for %s; error: %s' % (
                        employee.name, fields.Date.to_string(date), e))

    @api.model
    def capture_attendance_cron(self):
        for rec in self.search([]):
            logs = self.env['hr.biometric.log'].search([('bio_connect_id', '=', rec.id),
                                                               ('log_processed', '=', False)])
            if logs:
                start = datetime.strptime(min(logs.mapped('bio_timestamp')), '%Y-%m-%d %H:%M:%S').date()
                end = datetime.now().date()
                for x in range((end - start).days + 1):
                    dts = start + timedelta(days=x)
                    logs, res = self.action_process_attendance_cron(dts)
                    # method to create dummy/absent records for which biometric entry is not present in DB
                    # create absent attendance record for those employees
                    self.action_absent_employee_attendance_cron(dts)
                    attendance_obj = self.env['hr.attendance']
                    for employee, check_in, check_out, is_absent in res['attendance']:
                        
                        print ("EMP:::::::::::::::::", employee, check_in, check_out, is_absent)
                        
                        if check_in <= check_out:
                            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
        
                            last_attendance_before_check_in = self.env['hr.attendance'].search(
                                [('employee_id', '=', employee.id), ('check_in', '<=', check_in), ], order='check_in desc',
                                limit=1)
                            # new time-in between time-in and time-out
                            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out >= check_in:
                                # Overwrite absent attendance
                                vals = {}
                                vals['check_in'] = check_in
                                vals['check_out'] = check_out
                                vals['remarks'] = ''
                                vals['is_raw'] = True
                                if is_absent:
                                    vals['is_absent'] = True
        
                                if last_attendance_before_check_in.is_absent:
                                    vals['is_absent'] = False
                                if True:
                                    last_attendance_before_check_in.write(vals)
                                #except:
                                #    _logger.info('FAILED TO WRITE')
                                #    pass
                                continue
        
                            if not check_out:
                                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                                no_check_out_attendances = self.env['hr.attendance'].search([
                                    ('employee_id', '=', employee.id),
                                    ('check_out', '=', False),
                                ])
                                if no_check_out_attendances:
                                    pass
        
                            else:
                                # we verify that the latest attendance with check_in time before our check_out time
                                # is the same as the one before our check_in time computed before, otherwise it overlaps
                                last_attendance_before_check_out = self.env['hr.attendance'].search([
                                    ('employee_id', '=', employee.id),
                                    ('check_in', '<', check_out),
                                ], order='check_in desc', limit=1)
                                # get last attendance before this new attendance
                                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
        
                                    # Overwrite absent attendance
                                    vals = {}
        
                                    vals['check_in'] = check_in
                                    vals['check_out'] = check_out
                                    vals['remarks'] = ''
                                    vals['is_raw'] = True
        
                                    if is_absent:
                                        vals['is_absent'] = True
        
                                    if last_attendance_before_check_out.is_absent:
                                        vals['is_absent'] = False
                                    if True:
                                        last_attendance_before_check_out.write(vals)
                                    #except:
                                    #    _logger.info('FAILED TO WRITE')
                                    #    pass
        
                                    continue
        
                            cutoff_start = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                                res['from_utc']))
                            cutoff_end = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                                res['to_utc']))
        
                            dt_start = cutoff_start.replace(hour=0, minute=0, second=0)
                            dt_end = cutoff_end.replace(hour=7, minute=0, second=0) + timedelta(days=1)
                            check_in2 = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(check_in))
        
                            # print employee.name,dt_start,check_in2,dt_end
                            # Only process logs within the payroll cutoff and write it as raw log
                            _logger.info(
                                'Creating attendance logs of employee %s with %s - %s ' % (
                                    employee.name, check_in, check_out))
                            attendance_obj.create({'employee_id': employee.id,
                                                   'check_in': check_in,
                                                   'check_out': check_out,
                                                   'is_raw': True,
                                                   'is_absent': is_absent or False})
                    attendance_obj.make_absent(res['from_utc'], res['to_utc'])
                    for log in logs:
                        log.write({'log_processed': True})
        return True

    @api.model
    def capture_night_shift_attendance_cron(self):
        for rec in self.search([]):
            logs = self.env['hr.biometric.log'].search([('bio_connect_id', '=', rec.id),
                                                               ('log_processed', '=', False)])
            if logs:
                # start = datetime.strptime(min(logs.mapped('bio_timestamp')), '%Y-%m-%d %H:%M:%S').date()
                start = datetime.strptime('2022-02-28 00:00:00', '%Y-%m-%d %H:%M:%S').date()
                end = datetime.now().date()
                for x in range((end - start).days + 1):
                    dts = start + timedelta(days=x)
                    logs, res = self.action_process_attendance_cron(dts, True)
                    # method to create dummy/absent records for which biometric entry is not present in DB
                    # create absent attendance record for those employees
                    self.action_absent_employee_attendance_cron(dts, True)
                    attendance_obj = self.env['hr.attendance']
                    for employee, check_in, check_out, is_absent in res['attendance']:

                        print ("EMP:::::::::::::::::", employee, check_in, check_out, is_absent)

                        if check_in <= check_out:
                            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
        
                            last_attendance_before_check_in = self.env['hr.attendance'].search(
                                [('employee_id', '=', employee.id), ('check_in', '<=', check_in), ], order='check_in desc',
                                limit=1)
                            # new time-in between time-in and time-out
                            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out >= check_in:
                                # Overwrite absent attendance
                                vals = {}
                                vals['check_in'] = check_in
                                vals['check_out'] = check_out
                                vals['remarks'] = ''
                                vals['is_raw'] = True
                                if is_absent:
                                    vals['is_absent'] = True

                                if last_attendance_before_check_in.is_absent:
                                    vals['is_absent'] = False
                                if True:
                                    last_attendance_before_check_in.write(vals)
                                continue

                            if not check_out:
                                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                                no_check_out_attendances = self.env['hr.attendance'].search([
                                    ('employee_id', '=', employee.id),
                                    ('check_out', '=', False),
                                ])
                                if no_check_out_attendances:
                                    pass

                            else:
                                # we verify that the latest attendance with check_in time before our check_out time
                                # is the same as the one before our check_in time computed before, otherwise it overlaps
                                last_attendance_before_check_out = self.env['hr.attendance'].search([
                                    ('employee_id', '=', employee.id),
                                    ('check_in', '<', check_out),
                                ], order='check_in desc', limit=1)
                                # get last attendance before this new attendance
                                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:

                                    # Overwrite absent attendance
                                    vals = {}

                                    vals['check_in'] = check_in
                                    vals['check_out'] = check_out
                                    vals['remarks'] = ''
                                    vals['is_raw'] = True

                                    if is_absent:
                                        vals['is_absent'] = True

                                    if last_attendance_before_check_out.is_absent:
                                        vals['is_absent'] = False
                                    if True:
                                        last_attendance_before_check_out.write(vals)
                                    #except:
                                    #    _logger.info('FAILED TO WRITE')
                                    #    pass

                                    continue

                            cutoff_start = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                                res['from_utc']))
                            cutoff_end = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                                res['to_utc']))

                            dt_start = cutoff_start.replace(hour=0, minute=0, second=0)
                            dt_end = cutoff_end.replace(hour=7, minute=0, second=0) + timedelta(days=1)
                            check_in2 = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(check_in))

                            # print employee.name,dt_start,check_in2,dt_end
                            # Only process logs within the payroll cutoff and write it as raw log
                            _logger.info(
                                'Creating attendance logs of employee %s with %s - %s ' % (
                                    employee.name, check_in, check_out))
                            attendance_obj.create({'employee_id': employee.id,
                                                   'check_in': check_in,
                                                   'check_out': check_out,
                                                   'is_raw': True,
                                                   'is_absent': is_absent or False})
                    # attendance_obj.make_absent(res['from_utc'], res['to_utc'])
                    for log in logs:
                        log.write({'log_processed': True})
        return True
