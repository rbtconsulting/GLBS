from odoo import fields, models, api
from datetime import date,datetime
import xlwt
import base64
import cStringIO
# from decorator import append

class AnnualizationReport(models.TransientModel):
    _name = 'hr.annualization.report'
    _description = 'Generate Annualization Report of Employees'

    @api.onchange('employee_ids')
    def get_resigned_employee_ids(self):
        resigned_emp_ids = []
        for emp in self.employee_ids:
            resigned_emp_ids.append(emp.id)
        self.emp_ids = resigned_emp_ids
    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y-%m-%d')

    def generate_report(self):
        self.ensure_one()
        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Alphabetical List Report', cell_overwrite_ok=True)
        fp = cStringIO.StringIO()
        xlwt.add_palette_colour("custom_colour", 0x21)
        wb1.set_colour_RGB(0x21, 98, 96, 96)
        company = self.env['res.company']._company_default_get('hris')
        date_from = self.date_from
        date_to = self.date_to

        header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; align: horiz center; pattern: pattern solid, fore_colour gray25;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        title_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")

        values = self.env['hr.annulization_structure.config'].generate_values(self.employee_ids, date_from, date_to, 'annualization-report')
        row = 0
        col = 0
        bir_list = []
        list = []
        for line in values['annualization_list']:
            if line.computation not in bir_list:
                list.append(line)
                bir_list.append(line.computation)

        for column in values['annulization_type']:
            filtered_records = []
            for record in list:
                if record.annulization_type == column[0]:
                    filtered_records.append(record)
            ws1.write_merge(row, row, col+1, col + len(filtered_records), column[1], header_style)
            col = (col + len(filtered_records))
        row_line = row + 1
        ws1.write(row_line, 0, "Employee", header_style)
        col = 0
#         bir_list = []
        for line in list:
            col += 1
#             if line.computation not in bir_list:
            ws1.write(row_line, col, line.name, title_style)
#                 bir_list.append(line.computation)
        for vals in values['values']:
            col = 0
            row_line += 1
            for value in vals:
                ws1.write(row_line, col, value, row_style)
                col += 1
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': out, 'name': 'annualization.xls'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Annualization Report',
            'res_model': 'hr.annualization.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def action_generate_xls_report(self):
        return self.generate_report()

    date_from = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    date_to = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    employee_ids = fields.Many2many('hr.employee', 'hr_annualization_rel', 'hr_annualization_id', 'employee_id', string='Employees',
                                    required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    emp_ids = fields.Char(string="Employee ids")
