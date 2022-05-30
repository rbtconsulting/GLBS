# -*- coding:utf-8 -*-
from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from dateutil.relativedelta import relativedelta 
import xlwt
import base64
import cStringIO

class AlphaListReport(models.TransientModel):
    _name = 'hr.alphalist.report'
    _description = 'HR Alpha List Report'
    
    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y-%m-%d')

    def calculate_ytd_amount(self,employee,ytd,record):
        ytd_amount = 0.0
        if record.ytd_config_ids and ytd and (not record.earner_type or (
            record.earner_type and employee.contract_id.earner_type == record.earner_type)):
            #Will get the previous year to date
            if record.prev_record:
                previous_ytd_amount = sum(ytd.year_to_date_line.filtered(lambda l: l.ytd_config_id in record.ytd_config_ids).mapped('old_ytd_amount')) or 0.0
                ytd_amount += previous_ytd_amount
            else:
                current_ytd_amount = sum(ytd.year_to_date_line.filtered(lambda l: l.ytd_config_id in record.ytd_config_ids).mapped('current_ytd_amount')) or 0.0
                ytd_amount += current_ytd_amount
        return ytd_amount

    def _get_alphalist_all(self, list_type):
        wb1 = xlwt.Workbook(encoding='utf-8')
        titles = dict(self.fields_get(allfields=['alphalist_type'])['alphalist_type']['selection'])
        for type in list_type:
            ws1 = wb1.add_sheet(type, cell_overwrite_ok=True)
            fp = cStringIO.StringIO()
            xlwt.add_palette_colour("custom_colour", 0x21)
            wb1.set_colour_RGB(0x21, 98, 96, 96)
            company = self.env['res.company']._company_default_get('hris')
            header_content_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
            header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;")
            category_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; align: horiz center;")
            row_style = xlwt.easyxf("font: name Helvetica, height 170;")
            total_row_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz right")
            title_style = xlwt.easyxf("font: name Helvetica size 30 px, bold 1, height 200;")
            total_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;pattern: pattern solid, fore_colour gray25;align: horiz right")
            
            alphalist_type = self.env['hr.alpha_list.main_config'].search([('alphalist_type', '=', type)], limit=1)
            config_line_len = 5 + len(alphalist_type.config_line)
            title = titles[type].upper()

            row = 1
            ws1.write_merge(row, row, 0, config_line_len,"{}{}".format(' '*(config_line_len), title), title_style)
            row += 5
            
            row += 1
            
            alphalist_config = self.env['hr.alpha_list.main_config'].search([('alphalist_type', '=', type)], limit=1)
            ws1.write(row, 0, "SEQ NO.", header_style)
            ws1.write(row, 1, "TIN", header_style)
            ws1.write(row, 2, "Last Name", header_style)
            ws1.write(row, 3, "First Name", header_style)
            ws1.write(row, 4, "Middle Name", header_style)
            
            BEGIN_COL = 5
            if type == '7_5':
            
                ws1.write(row, 5, "Region No. Where Assigned", header_style)
                ws1.write(row, 6, "From", header_style)
                ws1.write(row, 7, "To", header_style)
                
                BEGIN_COL = 8
            
            col = BEGIN_COL
            # New Code
            category = self.env['hr.alphalist_config.category'].search([('parent_id', '=', False)])
            parent_col = BEGIN_COL
            config_line_ids = self.env['hr.alpha_list.config']
            for column in category:
                parent = alphalist_config.config_line.filtered(lambda l: l.categ_id == column)
                config_line_ids += parent
                len_parent = len(parent)
                col += len(parent)
                for record in column.categ_line:
                    child = alphalist_config.config_line.filtered(lambda l: l.categ_id == record)
                    if child:
                        ws1.write_merge(row-1, row-1, col, col + len(child) -1, record.name, category_header_style)
                        col += len(child)
                        config_line_ids += child
                    len_parent += len(child)
                if len_parent:
                    ws1.write_merge(row-2, row-2, parent_col, parent_col + len_parent - 1, column.name, category_header_style)
                    parent_col += len_parent
            config_line_ids += alphalist_config.config_line.filtered(lambda l: not l.categ_id)
    
            col = BEGIN_COL
            for rec in config_line_ids:
                ws1.write(row, col, rec.name, header_style)
                col += 1
    
            row += 1
            seq = 0
    
            total_amount = {}
            key_to_limit = False
            hr_employee = self.employee_ids
            date_from = ((datetime.strptime(str(self.date_from), DEFAULT_SERVER_DATE_FORMAT)).strftime('%Y-01-01'))
            date_to = ((datetime.strptime(str(self.date_to), DEFAULT_SERVER_DATE_FORMAT)).strftime('%Y-12-31'))
            if type == '7_1':
                terminated_employee = self.env['hr.contract'].search([])
                hr_employee = self.env['hr.employee'].search(['|', ('active', '=', False), ('active', '=', True)])
                hr_employee = terminated_employee.filtered(lambda l: l.employee_id.id in hr_employee.ids and
                    l.state == 'close' and l.date_end > date_from and l.date_end < date_to).mapped('employee_id')
    
            elif type == '7_3':
                hr_ytd = self.env['hr.year_to_date'].search([])
                hr_employee = hr_ytd.filtered(lambda l: l.employee_id.id in hr_employee.ids and not l.previous_employer and
                                              (l.ytd_date >= date_from and l.ytd_date <= date_to)).mapped('employee_id')
    
            elif type == '7_4':
                hr_ytd = self.env['hr.year_to_date'].search([])
                hr_employee = hr_ytd.filtered(lambda l: l.employee_id.id in hr_employee.ids and l.previous_employer and
                                              (l.ytd_date >= date_from and l.ytd_date <= date_to)).mapped('employee_id')
    
            elif type == '7_5':
                hr_contract = self.env['hr.contract'].search([])
                hr_employee = hr_contract.filtered(lambda l: l.employee_id.id in hr_employee.ids and
                    l.date_start <= self.date_to and l.earner_type == 'mmw').mapped('employee_id')
    
            start_date = ((datetime.strptime(str(self.date_to), DEFAULT_SERVER_DATE_FORMAT)).strftime('%Y-1-1'))
            end_date = ((datetime.strptime(str(self.date_to), DEFAULT_SERVER_DATE_FORMAT)).strftime('%Y-12-31'))

            ytd_ids = self.env['hr.year_to_date'].search([('ytd_date','>=',date_from),
                                                      ('ytd_date','<=',date_to)])
            payslip_ids = self.env['hr.payslip'].search([('date_release', '>=', self.date_from),
                                                         ('date_to', '<=', self.date_to), ('state', '=', 'done'),
                                                         ('credit_note', '=', False)])
    
            for employee in hr_employee.sorted(key=lambda r:r.lastname):
                alpha_list = {}
                seq += 1
                ws1.write(row, 0, seq, row_style)
                ws1.write(row, 1, employee.identification_id or "", row_style)
                ws1.write(row, 2, employee.lastname or "", row_style)
                ws1.write(row, 3, employee.firstname or "", row_style)
                ws1.write(row, 4, employee.middlename or "", row_style)
                
                if type == '7_5' or type == 'all': 
                    ws1.write(row, 5, self.env['hr.employee.work_location'].get_region_name(employee.work_location_id.region) or "", row_style)
                    ws1.write(row, 6, employee.contract_id.date_start, row_style)
                    ws1.write(row, 7, employee.contract_id.date_end or 'Present', row_style)
    
                ytd = ytd_ids.filtered(lambda l: l.employee_id == employee)
                payslip = payslip_ids.filtered(lambda l: l.employee_id == employee)
                if payslip:
    
                    result = self.env['hr.payslip.line'].read_group([('slip_id', 'in', payslip.ids)], ['code', 'amount'], ['code'])
                    payslip_line = dict((data['code'], data['amount']) for data in result)
                    col_counter = BEGIN_COL
                    
                    #Non Taxable Limit
                    total_nontax_limit = float(self.env['ir.config_parameter'].get_param('non.tax.limit','0'))
                    
                    total_amount_limit = 0
    
                    #Get the configuration and do the computation based on the configuration
                    for record in config_line_ids:
                        rule_ids = {}
                        rule_ids[record.code] = record.rule_ids.mapped('code')
    
                        key, values = rule_ids.items()[0]
                        amount = self.compute_alphalist_config_amount(record, payslip_line, employee, ytd, values)
                        #Compute Total of Each Record
                        alpha_list[record.id] = amount
                        #A boolean value 
                        if record.boolean_value:
                            ws1.write(row, col_counter, record.boolean_value and 'YES' or 'NO', total_row_style)
                        else:
                            ws1.write(row, col_counter, "{:,.2f}".format(amount), total_row_style)
                        #Store one key
                        if record.include_excess:
                            key_to_limit = row,col_counter,amount,key
                        #Sum all columns tag with limit
                        if record.include_limit:
                            total_amount_limit += amount
                        
                        #Computes the grand total
                        if key in total_amount:
                            total_amount[key] = total_amount.get(key, 0) + amount
                        else:
                            total_amount[key] = amount
    
                        #Increment to the next column
                        col_counter += 1
                #Get the excess of the non taxable limit and add to the specified total taxable column
                if key_to_limit and total_amount_limit > total_nontax_limit:
                    excess = total_amount_limit - total_nontax_limit
                    
                    #Avoid confusion with the internal variable after unpack
                    _row,_col,_amount,_key = key_to_limit
                    #Add the excess to the total
                    total_amount[_key] = total_amount.get(_key, 0) + excess
                    
                    #Add the excess to that column
                    excess += _amount
                    ws1.write(_row, _col, "{:,.2f}".format(excess), total_row_style)
                    
                row += 1
                             
            row += 1
            ws1.write_merge(row, row, 0, BEGIN_COL - 1, "TOTAL", header_style)
            
            #Display all totals on the footer per column 
            col = BEGIN_COL
            for line in config_line_ids:
                if line.code in total_amount:
                    ws1.write(row, col, "{:,.2f}".format(total_amount[line.code]) , total_style)
                    col += 1
    
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        return out

    def generate_report(self):
        self.ensure_one()
#         .
        if self.alphalist_type and not self.alphalist_type == 'all':
            alphalist = self._get_alphalist_all([self.alphalist_type])
            self.write({'state': 'done', 'report': alphalist, 'name': '{}-alpha_list_details.xls'.format(self.alphalist_type)})

        elif self.alphalist_type == 'all':
            alphalist_all = self._get_alphalist_all(['7_1', '7_3', '7_4', '7_5'])
            self.write({'state': 'done', 'report': alphalist_all, 'name': '{}-alpha_list_details.xls'.format(self.alphalist_type)})

        return {
            'type': 'ir.actions.act_window',
            'name': 'AlphaList Report',
            'res_model': 'hr.alphalist.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def compute_alphalist_config_amount(self, record, payslip_line, employee, ytd, values):
        amount = 0.0
        if not record.earner_type or (record.earner_type and employee.contract_id.earner_type == record.earner_type):
            #Amount based on the salary rules
            amount = sum([payslip_line.get(code, 0) for code in set(values)])
        amount = amount or 0
        
        #Hierarchical structure
        if record.config_ids:
            total_config_amount = 0
            for conf in record.config_ids:
                total_config_amount += self.compute_alphalist_config_amount(conf, payslip_line, employee, ytd, values)
            amount += total_config_amount

        if record.condition_operator and record.config_ids2:
            total_config_amount2 = 0
            for conf in record.config_ids2:
                total_config_amount2 += self.compute_alphalist_config_amount(conf, payslip_line, employee, ytd, values)
            #Either add or subtract the current amount
            if record.condition_operator == '-':
                amount -= total_config_amount2
            else:
                amount += total_config_amount2

        #Year to date
        if record.ytd_config_ids:
            #Will get the previous year to date
            amount += self.calculate_ytd_amount(employee,ytd,record)
        return amount

    @api.multi
    def action_generate_xls_report(self):
        return self.generate_report()
    
    date_payroll = fields.Date(string='Payroll Date', required=True, default=_get_default_end_date)
    date_from = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    date_to = fields.Date(string='End Date', required=True, default=_get_default_end_date)
    employee_ids = fields.Many2many('hr.employee', 'alphalist_rel', 'alphalist_id', 'employee_id', string='Employees',
                                    required=True)
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    state = fields.Selection([('draft', 'Draft'), ('done', ' Done')], 'State', default='draft')
    job_id = fields.Many2one('hr.job', string='Job Title')
    company_id = fields.Many2one('res.company', string='Company')
    alphalist_type = fields.Selection([('7_1', 'Alphalist of Employees Terminated before December 31'), 
                                       ('7_3', 'Alphalist of Employees as of December 31 with No Previous Employer/s within the Year'), 
                                       ('7_4', 'Alphalist of Employees as of December 31 with Previous Employer/s within the Year'), 
                                       ('7_5', 'Alphalist of Employees who are Minimum Wage Earners'),
                                       ('all', 'All')], 
                                      'Alphalist Type', required=True)
    