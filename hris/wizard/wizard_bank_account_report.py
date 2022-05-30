# -*- coding:utf-8 -*-

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
import cStringIO
from odoo.exceptions import ValidationError
from datetime import datetime

from odoo import tools


class HRGenerateTextFile(models.TransientModel):
    _name = 'hr.bank.account'
    _description = 'HR Bank Account'


    # BDO bank FORMAT
    def action_generate_txt_report(self):
        emp = self.env['hr.payslip'].search([('employee_id', 'in', self.employee_ids.ids),
                                             ('date_release', '=', self.date_release), 
                                             ('credit_note', '=', False),
                                             ('state', '=', 'done')])
        employee_ids = {}
        for res in emp:
            result = self.env['hr.payslip.line'].read_group([('id', 'in', res.line_ids.ids)], ['code', 'amount'],['code'])
            line= dict((data['code'], data['amount']) for data in result)
            fnp = line.get('FNP', 0.0)
            if res.employee_id.id in employee_ids:
                employee_ids[res.employee_id.id] = employee_ids.get(res.employee_id.id, 0) + fnp
            else:
                employee_ids[res.employee_id.id] = fnp
        text_file = open('/tmp/bank_account.txt', 'wa')
        for emp_id, fnp in sorted(employee_ids.items(), key=lambda k:k[1]):
            emp = self.env['hr.employee'].browse(emp_id)


            text_file.write(str(emp.bank_account_id.acc_number or '') + '\t' + str(fnp) + '\n')
        text_file.close()
        with open('/tmp/bank_account.txt', 'rb') as f_read:
            file_data = f_read.read()
            out = base64.b64encode(file_data)
        self.write({'state': 'done', 'report': out, 'name': str(self.upload_date) +'.txt'})
        return  {
            'name': 'bank_account.txt',
            'res_model': 'hr.bank.account',
            'res_id': self.id,
            'type': 'ir.actions.act_windows',
             'view_mode':'form',
            'view_type':'form',
            'views': [(False, 'form')],


           }

    @api.onchange('payroll_period_id')
    def onchange_payroll_period(self):
        if self.payroll_period_id:
            self.date_release = self.payroll_period_id.date_release

    employee_ids = fields.Many2many('hr.employee', 'bank_account_rel', 'bank_account_id', 'employee_id', string='Employees', required=True)
    date_release = fields.Date('Date Release', required=True)
    upload_date = datetime.now().strftime("%m%d%y")
    payroll_period_id = fields.Many2one('hr.payroll.period_line', 'Payroll Period', required=True)
    report = fields.Binary('Prepared file', readonly=True)
    name = fields.Char('File Name', size=32)
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')

#BANK FILE EXCEL   
class BNKACCOUNT(models.TransientModel):
    _name = 'hr.bank.account.excel'
    _description = 'HR BANK ACCOUNT'

    @api.multi
    def action_generate_xls_report(self):
        self.ensure_one()
        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('BANK ACCOUNT')
        fp = cStringIO.StringIO()
        xlwt.add_palette_colour("custom_colour", 0x21)
        wb1.set_colour_RGB(0x21, 243, 20, 28)
        company = self.env['res.company']._company_default_get('hris')

        header_content_style = xlwt.easyxf("font: name Helvetica size 25 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        header_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour yellow;")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour yellow;align: horiz right")
        
        row = 0
        col = 0
        ws1.write(row, col + 0, "CURRENCY", row_style)
        ws1.write(row, col + 1, "EMPLOYER ACCT#", row_style)
        ws1.write(row, col + 2, "PAY CODE", row_style)
        ws1.write(row, col + 3, "EMP. ACCT.#", row_style)
        ws1.write(row, col + 4, "AMOUNT", row_style)
        ws1.write(row, col + 5, "SURNAME", row_style)
        ws1.write(row, col + 6, "FIRSTNAME", row_style)
        row += 1
        
        for employee in self.employee_ids:           
            payslip = self.env['hr.payslip'].search([('employee_id', '=', employee.id), ('credit_note', '=', False),
                            ('payroll_period_id', '=', self.payroll_period_id.id), ('state', '=', 'done') ])
            
            line_netpay = payslip.line_ids.filtered(lambda r:r.code == 'FNP')
                
            ws1.write(row, col + 0, '001', row_style)
            ws1.write(row, col + 1, '002060027865', row_style)
            ws1.write(row, col + 2, '1', row_style)
            ws1.write(row, col + 3, str(employee.bank_account_id.acc_number) , row_style)
            ws1.write(row, col + 4, str(line_netpay.amount), row_style)
            ws1.write(row, col + 5, str(employee.lastname), row_style)
            ws1.write(row, col + 6, str(employee.firstname), row_style)
            row += 1
            
        wb1.save(fp)    
        
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': out, 'name': 'BankAccount.xls'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'BANK ACCOUNT',
            'res_model': 'hr.bank.account.excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
    @api.onchange('payroll_period_id')
    def onchange_payroll_period(self):
        if self.payroll_period_id:
            self.date_release = self.payroll_period_id.date_release

    employee_ids = fields.Many2many('hr.employee', 'bank_account_rel1', 'bank_account_id', 'employee_id', string='Employees')
    date_release = fields.Date('Date Release', required=True)
    upload_date = datetime.now().strftime("%m%d%y")
    payroll_period_id = fields.Many2one('hr.payroll.period_line', 'Payroll Period', required=True)
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')


# BANK FILE EXCEL
class BNKACCOUNTMetroBank(models.TransientModel):
    _name = 'hr.bank.metrobank'
    _description = 'Metro Bank'

    @api.multi
    def action_generate_xls_report(self):
        self.ensure_one()
        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('BANK ACCOUNT')
        fp = cStringIO.StringIO()
        xlwt.add_palette_colour("custom_colour", 0x21)
        wb1.set_colour_RGB(0x21, 243, 20, 28)
        company = self.env['res.company']._company_default_get('hris')

        header_content_style = xlwt.easyxf("font: name Helvetica size 25 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        header_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour yellow;")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")

        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        total_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour yellow;align: horiz right")

        row = 1
        col = 0
        ws1.write_merge(row, row, 3, 6, "METROBANK REPORT", header_content_style)
        row += 2
        ws1.write(row, col + 0, "From :", sub_header_style)
        ws1.write(row, col + 1, datetime.strftime(datetime.strptime(self.payroll_period_id.start_date,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row, col + 0, "To :", sub_header_style)
        ws1.write(row, col + 1, datetime.strftime(datetime.strptime(self.payroll_period_id.end_date,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 2
        ws1.write(row, col + 0, "Lastname", row_style)
        ws1.write(row, col + 1, "Firstname", row_style)
        ws1.write(row, col + 2, "Middle Name", row_style)
        ws1.write(row, col + 3, "Employee Account Number", row_style)
        ws1.write(row, col + 4, "Amount", row_style)
        row += 1

        for emp in self.employee_ids:
            payslip = self.env['hr.payslip'].search([('employee_id', '=', emp.id),
                                                     ('payroll_period_id', '=', self.payroll_period_id.id),
                                                     ('state', '=', 'done')], limit=1)
            employee = self.env['hr.employee'].browse(emp.id)
            line_netpay = payslip.line_ids.filtered(lambda r: r.code == 'FNP')
            ws1.write(row, col + 0, employee.lastname, row_style)
            ws1.write(row, col + 1, employee.firstname, row_style)
            ws1.write(row, col + 2, employee.middlename, row_style)
            ws1.write(row, col + 3, employee.bank_account_id.acc_number, row_style)
            ws1.write(row, col + 4, line_netpay.amount, row_style)

            row += 1

        wb1.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': out, 'name': 'metrobank.xls'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'MetroBank',
            'res_model': 'hr.bank.metrobank',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.onchange('payroll_period_id')
    def onchange_payroll_period(self):
        if self.payroll_period_id:
            self.date_release = self.payroll_period_id.date_release

    employee_ids = fields.Many2many('hr.employee', 'metrobank_rel1', 'bank_account_id', 'employee_id',
                                    string='Employees')
    date_release = fields.Date('Date Release', required=True)
    upload_date = datetime.now().strftime("%m%d%y")
    payroll_period_id = fields.Many2one('hr.payroll.period_line', 'Payroll Period', required=True)
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    
#YTDREPORTEXCELTOTAL    
class YTDreportTotal(models.TransientModel):
    _name = 'hr.ytd.report.total'
    _description = 'Generate YTD Report TOTAL of Employees'
    
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
        
        header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        title_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")
        
        alphalist_type = self.env['hr.year_to_date.config'].search([])  
        row = 1
        row += 1
        ytd_config = self.env['hr.year_to_date.config'].search([]) 
        ws1.write(row, 0, "SEQ NO.", header_style)
        ws1.write(row, 1, "Employee ID", header_style)
        ws1.write(row, 2, "Last Name", header_style)
        ws1.write(row, 3, "First Name", header_style)
        ws1.write(row, 4, "Middle Name", header_style)
        
        BEGIN_COL = 5      
        col = BEGIN_COL
        ytd_ids = []
        for rec in ytd_config:
            ws1.write(row, col, rec.name, header_style)
            ytd_ids.append(rec.id)
            col += 1
                    
        row += 1
        seq = 0
        
        total_amount = {}
        ytd_records = {}
        #ids stored archive and active
        emp_ids = self.emp_ids[1:-1]
        ids = emp_ids.split(',')
        for id in ids:
            employee = self.env['hr.employee'].browse(int(id))
            
            seq += 1
            ws1.write(row, 0, seq, row_style)
            ws1.write(row, 1, employee.barcode or "", row_style)
            ws1.write(row, 2, employee.lastname or "", row_style)
            ws1.write(row, 3, employee.firstname or "", row_style)
            ws1.write(row, 4, employee.middlename or "", row_style)
            
            ytd = self.env['hr.year_to_date'].search([('employee_id','=',employee.id),\
                                                             ('ytd_date','>=',self.date_from),('ytd_date','<=',self.date_to)
                                                             ],limit = 1)
            col_counter = BEGIN_COL
            for rec in ytd_config:
               
                amount = ytd.year_to_date_line.filtered(lambda x : x.ytd_config_id.id == rec.id)
                
                if amount:
                    if (rec.id,col_counter) in ytd_records:
                        ytd_records[rec.id,col_counter].append(amount)
                    else:
                        ytd_records[rec.id,col_counter] = [amount]
                    ws1.write(row, col_counter, "{:,.2f}".format(amount.amount_total), total_row_style)
                    
                    col_counter +=1
                else:
                    ws1.write(row, col_counter, "{:,.2f}".format(0.0), total_row_style)
                    col_counter +=1
        
            
            row += 1
                         
        #row += 1
        #ws1.write_merge(row, row, 0, BEGIN_COL - 1, "TOTAL", header_style)
        
        #Display all totals on the footer per column 
        #col = 5
        #for key, amount in ytd_records.items():
            #total_amount = sum([r.amount for r in amount])
            #ws1.write(row, key[-1], "{:,.2f}".format(total_amount) , total_style)
            #col += 1
            
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': out, 'name': 'YeartoDate.xls'})
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'YTD Report Total',
            'res_model': 'hr.ytd.report.total',
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
    employee_ids = fields.Many2many('hr.employee', 'hr_year_to_date_rel1', 'hr_year_to_date_id', 'employee_id', string='Employees', required=True)
    emp_ids = fields.Char(string="Employee ids")
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

#YTDreportOld
class YTDreportOld(models.TransientModel):
    _name = 'hr.ytd.report.old'
    _description = 'Generate YTD Report Old of Employees'
    
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
        
        header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        title_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")
        
        alphalist_type = self.env['hr.year_to_date.config'].search([])  
        row = 1
        row += 1
        ytd_config = self.env['hr.year_to_date.config'].search([]) 
        ws1.write(row, 0, "SEQ NO.", header_style)
        ws1.write(row, 1, "Employee ID", header_style)
        ws1.write(row, 2, "Last Name", header_style)
        ws1.write(row, 3, "First Name", header_style)
        ws1.write(row, 4, "Middle Name", header_style)
        
        BEGIN_COL = 5      
        col = BEGIN_COL
        ytd_ids = []
        for rec in ytd_config:
            ws1.write(row, col, rec.name, header_style)
            ytd_ids.append(rec.id)
            col += 1
                    
        row += 1
        seq = 0
        
        total_amount = {}
        ytd_records = {}
        #ids stored archive and active
        emp_ids = self.emp_ids[1:-1]
        ids = emp_ids.split(',')
        for id in ids:
            employee = self.env['hr.employee'].browse(int(id))
            
            seq += 1
            ws1.write(row, 0, seq, row_style)
            ws1.write(row, 1, employee.barcode or "", row_style)
            ws1.write(row, 2, employee.lastname or "", row_style)
            ws1.write(row, 3, employee.firstname or "", row_style)
            ws1.write(row, 4, employee.middlename or "", row_style)
            
            ytd = self.env['hr.year_to_date'].search([('employee_id','=',employee.id),\
                                                             ('ytd_date','>=',self.date_from),('ytd_date','<=',self.date_to)
                                                             ],limit = 1)
            col_counter = BEGIN_COL
            for rec in ytd_config:
               
                amount = ytd.year_to_date_line.filtered(lambda x : x.ytd_config_id.id == rec.id)
                
                if amount:
                    if (rec.id,col_counter) in ytd_records:
                        ytd_records[rec.id,col_counter].append(amount)
                    else:
                        ytd_records[rec.id,col_counter] = [amount]
                    ws1.write(row, col_counter, "{:,.2f}".format(amount.old_ytd_amount), total_row_style)
                    
                    col_counter +=1
                else:
                    ws1.write(row, col_counter, "{:,.2f}".format(0.0), total_row_style)
                    col_counter +=1
        
            
            row += 1
                         
        #row += 1
        #ws1.write_merge(row, row, 0, BEGIN_COL - 1, "TOTAL", header_style)
        
        #Display all totals on the footer per column 
        #col = 5
        #for key, amount in ytd_records.items():
            #total_amount = sum([r.amount for r in amount])
            #ws1.write(row, key[-1], "{:,.2f}".format(total_amount) , total_style)
            #col += 1
            
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': out, 'name': 'OldYeartoDate.xls'})
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'YTD Report Old',
            'res_model': 'hr.ytd.report.old',
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
    employee_ids = fields.Many2many('hr.employee', 'hr_year_to_date_rel2', 'hr_year_to_date_id', 'employee_id', string='Employees', required=True)
    emp_ids = fields.Char(string="Employee ids")
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

#YTDreportCurrent
class YTDreportOld(models.TransientModel):
    _name = 'hr.ytd.report.current'
    _description = 'Generate YTD Report Current of Employees'
    
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
        
        header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;")
        row_style = xlwt.easyxf("font: name Helvetica, height 170;")
        total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
        title_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
        total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")
        
        alphalist_type = self.env['hr.year_to_date.config'].search([])  
        row = 1
        row += 1
        ytd_config = self.env['hr.year_to_date.config'].search([]) 
        ws1.write(row, 0, "SEQ NO.", header_style)
        ws1.write(row, 1, "Employee ID", header_style)
        ws1.write(row, 2, "Last Name", header_style)
        ws1.write(row, 3, "First Name", header_style)
        ws1.write(row, 4, "Middle Name", header_style)
        
        BEGIN_COL = 5      
        col = BEGIN_COL
        ytd_ids = []
        for rec in ytd_config:
            ws1.write(row, col, rec.name, header_style)
            ytd_ids.append(rec.id)
            col += 1
                    
        row += 1
        seq = 0
        
        total_amount = {}
        ytd_records = {}
        #ids stored archive and active
        emp_ids = self.emp_ids[1:-1]
        ids = emp_ids.split(',')
        for id in ids:
            employee = self.env['hr.employee'].browse(int(id))
            
            seq += 1
            ws1.write(row, 0, seq, row_style)
            ws1.write(row, 1, employee.barcode or "", row_style)
            ws1.write(row, 2, employee.lastname or "", row_style)
            ws1.write(row, 3, employee.firstname or "", row_style)
            ws1.write(row, 4, employee.middlename or "", row_style)
            
            ytd = self.env['hr.year_to_date'].search([('employee_id','=',employee.id),\
                                                             ('ytd_date','>=',self.date_from),('ytd_date','<=',self.date_to)
                                                             ],limit = 1)
            col_counter = BEGIN_COL
            for rec in ytd_config:
               
                amount = ytd.year_to_date_line.filtered(lambda x : x.ytd_config_id.id == rec.id)
                
                if amount:
                    if (rec.id,col_counter) in ytd_records:
                        ytd_records[rec.id,col_counter].append(amount)
                    else:
                        ytd_records[rec.id,col_counter] = [amount]
                    ws1.write(row, col_counter, "{:,.2f}".format(amount.current_ytd_amount), total_row_style)
                    
                    col_counter +=1
                else:
                    ws1.write(row, col_counter, "{:,.2f}".format(0.0), total_row_style)
                    col_counter +=1
        
            
            row += 1
                         
        #row += 1
        #ws1.write_merge(row, row, 0, BEGIN_COL - 1, "TOTAL", header_style)
        
        #Display all totals on the footer per column 
        #col = 5
        #for key, amount in ytd_records.items():
            #total_amount = sum([r.amount for r in amount])
            #ws1.write(row, key[-1], "{:,.2f}".format(total_amount) , total_style)
            #col += 1
            
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'done', 'report': out, 'name': 'CurrentYeartoDate.xls'})
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'YTD Report Current',
            'res_model': 'hr.ytd.report.current',
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
    employee_ids = fields.Many2many('hr.employee', 'hr_year_to_date_rel3', 'hr_year_to_date_id', 'employee_id', string='Employees', required=True)
    emp_ids = fields.Char(string="Employee ids")
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32) 
