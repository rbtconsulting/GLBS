from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta 
import xlwt
import base64
import cStringIO
import pytz

class AttendanceReport(models.TransientModel):
    _name = 'hr.attendance.report'
    _description = 'HR Attendance Report'
    
    @api.multi
    def action_generate_xls_report(self):
        self.ensure_one()
        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Attendance Report', cell_overwrite_ok=True)
        fp = cStringIO.StringIO()
        header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        title_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")
        
        columns = ['','Employee','From','To','Actual Time In','Actual Time Out','Regular Hours',
                   'Absent','Late','Undertime','Remarks','Filed Time In','Filed Time Out','OB Hours','LWP Hours','LWOP Hours','Rest Day',
                   'Special Holiday','Regular Holiday','Night Shift Differential','OT Time In','OT Time Out','Regular Overtime',
                   'Rest Day Overtime','Special Holiday Overtime','Regular Holiday Overtime','Night Differential Overtime']
        columns_field = ['schedule_in', 'schedule_out','check_in','check_out',
                         'worked_hours','absent_hours','late_hours','undertime_hours','remarks','date_from','date_to','ob_hours',
                         'leave_hours','leave_wop_hours','rest_day_hours','sp_holiday_hours','reg_holiday_hours',
                         'night_diff_ot_hours','start_time','end_time','overtime_hours','rest_day_ot_hours','sp_hday_ot_hours',
                         'reg_hday_ot_hours','night_diff_ot_hours']
        row = 0
        count_col = 0
        for col in columns:
            ws1.write(row, count_col, col, header_style)
            count_col += 1

        sequence_no = 0
        attendance_ids = self.env['hr.attendance'].search([('employee_id', 'in', self.employee_ids.ids), ('schedule_in', '=', self.date_from)])
        for attendance in attendance_ids:
            row += 1
            sequence_no += 1
            ws1.write(row, 0, sequence_no, )
            ws1.write(row, 1, attendance.employee_id.name, )
            count_col = 1
            timezone = pytz.timezone(self.env.context.get('tz') or 'UTC')
            for col in columns_field:
                count_col += 1
                if col in ['schedule_in', 'schedule_out','check_in','check_out']:
                    date_time = fields.Datetime.from_string(attendance[col]).replace(tzinfo=pytz.utc).astimezone(timezone)
                    ws1.write(row, count_col, date_time.strftime('%H:%M:%S'), )
                elif col in ['date_from','date_to']:
                    leave = attendance.leave_ids.filtered(lambda l: l.holiday_status_id.is_ob)
                    if leave:
                        date_time = fields.Datetime.from_string(leave[0][col]).replace(tzinfo=pytz.utc).astimezone(timezone)
                        ws1.write(row, count_col, date_time.strftime('%H:%M:%S'), )
                    else:
                        ws1.write(row, count_col,'', )
                elif col in ['start_time','end_time']:
                    if attendance.overtime_id:
                        date_time = fields.Datetime.from_string(attendance.overtime_id[col]).replace(tzinfo=pytz.utc).astimezone(timezone)
                        ws1.write(row, count_col, date_time.strftime('%H:%M:%S'), )
                    else:
                        ws1.write(row, count_col,'', )
                else:
                    ws1.write(row, count_col, attendance[col], )

        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())

        self.write({'state': 'done', 'report': out, 'name': 'Attendance-report.xls'})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Report',
            'res_model': 'hr.attendance.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    date_from = fields.Date(string='Select Date', required=True)
    employee_ids = fields.Many2many('hr.employee', 'attendance_report_rel_template', 'attendance_id', 'employee_id', string='Employees',
                                    required=True, ondelete="restrict")
    name = fields.Char('File Name')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
