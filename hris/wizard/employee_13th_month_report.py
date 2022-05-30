#-*- coding:utf-8 -*-

from odoo import fields, models, api
import xlwt
import base64
import cStringIO

class HR13thMonth(models.TransientModel):
    _name = 'hr.13th.month'
    _description = 'HR 13th Month Report'

    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y-%m-%d')

    date_from = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    date_to = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    employee_ids = fields.Many2many('hr.employee', 'emp13th_month_rel', 'emp13th_month_id', 'employee_id', string='Employees', required=True)
    date_release_id = fields.Many2one('hr.payroll.period', 'Date Release', ondelete='cascade')

    names = fields.Integer(default=1)
    
    @api.multi
    def action_generate_excel(self, data):
        work_book = xlwt.Workbook(encoding='utf-8')
        work_sheet = work_book.add_sheet('13th Month Pay', cell_overwrite_ok=True)
        fp = cStringIO.StringIO()
        xlwt.add_palette_colour("custom_colour", 0x21)
        work_book.set_colour_RGB(0x21, 98, 96, 96)
        company = self.env['res.company']._company_default_get('hris')

        header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        title_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")
        
        report_details = self.env['report.hris.report_13thmonth_template'].get_13thmonth_details(data)
        
        row = 1
    
        dt_from = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_from)) 
        dt_to = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(self.date_to)) 
        
        work_sheet.write_merge(row, row, 0, 2, company.name)
        row += 2
        work_sheet.write_merge(row, row, 0, 2, '13th Month Report')
        row += 1
        work_sheet.write_merge(row, row, 0, 2, 'Period: {} - {}'.format(dt_from.strftime('%B %d, %Y'), dt_to.strftime('%B %d, %Y')))
        row += 2
        
        work_sheet.write(row, 0, "EMP No.", header_style)
        work_sheet.write(row, 1, "Name", header_style)
        work_sheet.write(row, 2, "Total", header_style)
        row += 1
        amount_total = 0
        
        #Details
        for record in report_details[:-1]:
            
            amount = record['emp13thmonth'] or 0
            work_sheet.write(row, 0, record['EMPLOYEE'].barcode or '', row_style)
            work_sheet.write(row, 1, record['EMPLOYEE'].name or '', row_style)
            work_sheet.write(row, 2, '{:,.2f}'.format(amount), total_row_style)
            
            amount_total += amount
            
            row += 1
        
        #Totals
        row += 1
        work_sheet.write_merge(row, row, 0, 1, 'TOTAL', total_style)
        work_sheet.write(row, 2,'{:,.2f}'.format(amount_total), total_style)
        row += 2
        
        #Approvers
        work_sheet.write(row, 0, 'Prepared By:', row_style)
        work_sheet.write(row, 1, 'Approved By:', row_style)
        work_sheet.write(row, 2, 'Checked By:', row_style)
                
        
        work_book.save(fp)
        report_file = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': report_file, 'name': '13th_month_pay.xls'})
        
        return {
            'type': 'ir.actions.act_window',
            'name': '13th Month Pay Report',
            'res_model': 'hr.13th.month',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
            }
        
    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        excel_report = self._context.get('excel_report')
        
        if excel_report:
            return self.action_generate_excel(data['form'])
        # id from hr_employee_bir_report.xml
        return self.env['report'].get_action(self, 'hris.report_13thmonth_template', data=data)
