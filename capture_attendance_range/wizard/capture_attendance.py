from odoo import fields, models, api
import datetime as dt
from odoo import fields, api, models, registry
from odoo.tools import mute_logger
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

import logging

_logger = logging.getLogger(__name__)


class CaptureAttendance(models.TransientModel):
    _name = "capture.attendance"

    branch_id = fields.Many2one('res.branch', String="Branch")
    bio_logs = fields.Many2one(
        'hr.biometric.connection', string="Biometrics Device")
    dt_from = fields.Datetime(string='Date From', required=True)
    dt_to = fields.Datetime(string='Date To', required=True)

    def rec_to_utc(self, to_convert):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError((
                'No timezone!\n\nConfigure your timezone\n\nClick your Profile Name>Preferences>Timezone(Asia/Manila)'))
        local = pytz.timezone('Asia/Manila')
        local_dt_log = local.localize(to_convert, is_dst=None)
        return local_dt_log.astimezone(pytz.utc)

    def check_bio_connection(self):
        domain = []
        if self.bio_logs:
            domain += [('id', '=', self.bio_logs.id)]
        device = self.env['hr.biometric.connection'].search(domain)
        for bio_device in device:
            if bio_device.state == 'disconnected':
                raise ValidationError(
                    ("biometric device for %s is disconnected!") % (self.bio_logs.name))
            else:
                bio_device.btn_get_attendance()

    @api.multi
    def action_process_attendance(self, from_dt):
        dt_from = from_dt - timedelta(days=1)
        dt_to = from_dt
        utc_dt_from = self.rec_to_utc(
            fields.Datetime.from_string(dt_from.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')))
        utc_dt_to = self.rec_to_utc(
            fields.Datetime.from_string(dt_to.replace(hour=1, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')))
        use_new_cursor = True
        if use_new_cursor:
            cr = registry(self._cr.dbname).cursor()
            self = self.with_env(self.env(cr=cr))

        attendances_list = []
        domain = []
        # if self.branch_id:
        #     domain += [('branch_id', '=', self.branch_id.id)]
        for employee in self.env['hr.employee'].search(domain):
            if not employee.barcode:
                _logger.info('Employee %s has no barcode.' % (employee.name))

                continue
            if not employee.barcode.isdigit():
                _logger.info('Employee %s barcode must be integer.' %
                             (employee.name))
                continue

            date_from_utc = utc_dt_from.strftime('%Y-%m-%d %H:%M:%S')
            date_to_utc = utc_dt_to.strftime('%Y-%m-%d %H:%M:%S')
            domain = [
                ('user_id', '=', str(employee.barcode)),
                ('bio_timestamp', '>=', date_from_utc),
                ('bio_timestamp', '<=', date_to_utc)
            ]
            if self.bio_logs:
                domain += [('bio_connect_id', '=', self.bio_logs.id)]
            attendance_record = {}
            for record in self.env['hr.biometric.log'].search(domain):
                local_timestamp = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                    record.bio_timestamp))
                date_log = local_timestamp.strftime('%Y-%m-%d')
                time_log = local_timestamp.strftime('%H:%M:%S')
                key = employee.barcode, date_log

                if key in attendance_record:
                    attendance_record[key].append(record)
                else:
                    attendance_record[key] = [record]
            if not attendance_record:
                _logger.info('Employee %s has no attendances.' %
                             (employee.name))
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
            attendances_list.append(
                (employee, list_time_in, list_time_out, is_absent))
            _logger.info('Processing the attendances.%s' % (employee.name))

        res = dict(attendance=attendances_list, from_utc=utc_dt_from,
                   to_utc=utc_dt_to, use_new_cursor=use_new_cursor)
        if use_new_cursor:
            self.env.cr.commit()
        return res

    @api.multi
    def capture_attendance(self):
        """Process timelogs and generate employee attendances and timekeeping."""
        start = datetime.strptime(self.dt_from, DEFAULT_SERVER_DATETIME_FORMAT)
        end = datetime.strptime(self.dt_to, DEFAULT_SERVER_DATETIME_FORMAT)

        list_of_dates = [start + timedelta(days=x)
                         for x in range((end - start).days + 1)]
        for dts in list_of_dates:
            res = self.action_process_attendance(dts)
            attendance_obj = self.env['hr.attendance']
            for employee, check_in, check_out, is_absent in res['attendance']:
                if check_in <= check_out:
                    # we take the latest attendance before our check_in time
                    # and check it doesn't overlap with ours

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
                        try:
                            with mute_logger('odoo.sql_db'):
                                last_attendance_before_check_in.write(vals)
                        except:
                            _logger.info('FAILED TO WRITE')
                            pass
                        continue

                    if not check_out:
                        # if our attendance is "open" (no check_out), we verify
                        # there is no other "open" attendance
                        no_check_out_attendances = self.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            ('check_out', '=', False),
                        ])
                        if no_check_out_attendances:
                            pass

                    else:
                        # we verify that the latest attendance with check_in time before our check_out time
                        # is the same as the one before our check_in time
                        # computed before, otherwise it overlaps
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
                            try:
                                with mute_logger('odoo.sql_db'):
                                    last_attendance_before_check_out.write(
                                        vals)
                            except:
                                _logger.info('FAILED TO WRITE')
                                pass

                            continue

                    cutoff_start = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                        res['from_utc'].strftime('%Y-%m-%d')))
                    cutoff_end = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(
                        res['to_utc'].strftime('%Y-%m-%d')))

                    dt_start = cutoff_start.replace(hour=0, minute=0, second=0)
                    dt_end = cutoff_end.replace(
                        hour=7, minute=0, second=0) + timedelta(days=1)
                    check_in2 = fields.Datetime.context_timestamp(
                        self, fields.Datetime.from_string(check_in))

                    # print employee.name,dt_start,check_in2,dt_end
                    # Only process logs within the payroll cutoff and write it
                    # as raw log
                    if res['from_utc'] <= check_in2 <= res['to_utc']:
                        try:
                            with mute_logger('odoo.sql_db'):

                                _logger.info(
                                    'Creating attendance logs of employee %s with %s - %s ' % (
                                        employee.name, check_in, check_out))
                                attendance_obj.create({'employee_id': employee.id,
                                                       'check_in': check_in,
                                                       'check_out': check_out,
                                                       'is_raw': True,
                                                       'is_absent': is_absent or False})

                        except:
                            _logger.info(
                                'FAILED TO CREATE attendance for %s' % (employee.name))

                            continue
                    if res['use_new_cursor']:
                        self.env.cr.commit()

            attendance_obj.make_absent(res['from_utc'].strftime('%Y-%m-%d %H:%M:%S'),
                                       res['to_utc'].strftime('%Y-%m-%d %H:%M:%S'))
