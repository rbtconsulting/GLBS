#-*- coding:utf-8 -*-

from odoo import api, fields, models, _

class HRAphalistStructure(models.Model):
    _name = 'hr.alpha_list.main_config'
    _description = 'Alpha List Structure'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active')
    config_line = fields.One2many('hr.alpha_list.config', 'alphalist_structure_id', 'Structure', copy=True)
    alphalist_type = fields.Selection([('7_1', 'Alphalist of Employees Terminated before December 31'), 
                                       ('7_3', 'Alphalist of Employees as of December 31 with No Previous Employer/s within the Year'), 
                                       ('7_4', 'Alphalist of Employees as of December 31 with Previous Employer/s within the Year'), 
                                       ('7_5', 'Alphalist of Employees who are Minimum Wage Earners')], 
                                      'Alphalist Type', required=True)


class HRAlphalistCategory(models.Model):
    _name = 'hr.alphalist_config.category'
    _order = 'sequence'

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValueError(_('Error ! You cannot create recursive categories.'))
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            
            rec = record
            name = rec.name
            while rec.parent_id:
                rec = rec.parent_id
                name = rec.name + '/' + name
                     
            res.append((record.id, name))
        return res
    
    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one('hr.alphalist_config.category', 'Parent Category')
    sequence = fields.Char('Sequence', default=lambda self: _('New'))
    categ_line = fields.One2many('hr.alphalist_config.category', 'parent_id', 'Child Categories')

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('alphalist.config.code')
        return super(HRAlphalistCategory, self).create(vals)


class HRAlphaListConfig(models.Model):
    _name = 'hr.alpha_list.config'
    _description = 'Alpha List Configuration'
    _order = "categ_id,code"
    
    name = fields.Char(string="Column Name",required=True)
    code = fields.Integer(string="Sequence",required=True)
    categ_id = fields.Many2one('hr.alphalist_config.category', 'Category')
    rule_ids = fields.Many2many('hr.salary.rule', 'hr_alpha_rule_rel', 'struct_id', 'rule_id', string='Salary Rules')
    alphalist_structure_id = fields.Many2one('hr.alpha_list.main_config', 'Structure')
    
    config_ids = fields.Many2many('hr.alpha_list.config', 'hr_alpha_config_ids_rel', 'alpha_config_id', 'config_id', string='Configuration')
    condition_operator = fields.Selection([('+', 'Plus'),('-', 'Minus')], 'Condition') 
    config_ids2 = fields.Many2many('hr.alpha_list.config', 'hr_alpha_config_ids_rel2', 'alpha_config_id', 'config_id', string='Configuration')
    
    ytd_config_ids = fields.Many2many('hr.year_to_date.config', 'hr_alpha_ytd_ids_rel', 'alpha_config_id', 'ytd_config_id', string='YTD Configuration')
    
    prev_record = fields.Boolean('Previous', help="If based on previous employer ytd.")
    boolean_value = fields.Boolean('Yes/No', help="If substitute filing.")
    
    earner_type = fields.Selection([('mmw','Minimum Wage Earner'),('nonmmw','Non Minimum Wage Earner')], 'Earner Type')
    include_limit = fields.Boolean('Include in Limit?', help="If True,will include add to non-taxable limit.")
    include_excess = fields.Boolean('Include Limit Excess?', help="If True,will include amount plus non-taxable excess value.")
 
class PayrollRegisterConfig(models.Model):
    _name = 'payroll.register.config'
    _description = 'Payroll Register Configuration'

    name = fields.Char('Name', required=True)
    config_line = fields.One2many('payroll.register.rule.config', 'payroll_register_rule_config_id', 'Columns')
    active = fields.Boolean('Active', default=True)
    
class PayrollRegisterRuleConfig(models.Model):
    _name = 'payroll.register.rule.config'
    _description = 'Payroll Register Rules Configuration'
    _order = 'sequence asc'
    
    name = fields.Char('Column Name', required=True)
    sequence = fields.Integer('Sequence')
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'payroll_reg_salary_rule_rel', 'payroll_reg_config_id', 'rule_id', 'Salary Rules')
    payroll_register_rule_config_id = fields.Many2one('payroll.register.config', 'Configuration', auto_join=True)
    from_salary_computation = fields.Boolean('Salary Computation')
    from_worked_days = fields.Boolean('Worked Days and Inputs')
    active = fields.Boolean('Active', default=True)

class HRPayslipTemplate(models.Model):
    _name ="hr.payslip.template"
    
    name = fields.Char('Name', default="Default", required=True)
    payslip_template = fields.Selection([('template_one','Template One'),
                                         ('template_two','Template Two')], default='template_one')
    
    report_template_id = fields.Many2one('ir.actions.report.xml', 'Report Template', required=True)
    holiday_status_ids = fields.Many2many('hr.holidays.status', 'payslip_holiday_rel', 'payslip_id', 'holiday_status_id', 'Leaves Included on Payslip')
    
    salary_rule_earnings = fields.Many2many('hr.salary.rule', 'payslip_earnings_rel', 'payslip_id', 'rule_id', 'Earnings')
    salary_rule_deductions = fields.Many2many('hr.salary.rule', 'payslip_deductions_rel', 'payslip_id', 'rule_id', 'Deductions')
    salary_rule_loans = fields.Many2many('hr.salary.rule', 'payslip_loans_rel', 'payslip_id', 'rule_id', 'Loans')
    salary_rule_earning_inputs = fields.Many2many('hr.rule.input', 'payslip_input_rel', 'payslip_id', 'rule_id', 'Earning Adjustments')
    salary_rule_deduction_inputs = fields.Many2many('hr.rule.input', 'payslip_input2_rel', 'payslip_id', 'rule_id', 'Deduction Adjustments')
    
    
class HR13thMonthPay(models.Model):
    _name = 'hr.th.month_pay.config'
    _description = 'Thirteenth Month Pay Template'
    
    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string='Active')
    config_line = fields.One2many('hr.th.month_pay.config.line','th_month_pay_id')

class HR13thMonthPayLine(models.Model):
    _name = 'hr.th.month_pay.config.line'
    _description = 'Thirteenth Month Pay Line'
    
    condition = fields.Selection([('add','Add'),('subtract','Subtract')],required=True ,string="Condition")
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'thirteenth_month_pay_rel', 'th_pay_id', 'rule_id', 'Salary Rules')
    ytd_config_ids = fields.Many2many('hr.year_to_date.config', 'thirteenth_month_pay_ytd_rel', 'th_pay_id', 'year_to_date_config_id', ' Year to Date')
    th_month_pay_id = fields.Many2one('hr.th.month_pay.config', string="TH Month Pay")

class HRYearToDateConfig(models.Model):
    _name = 'hr.year_to_date.config'
    _description = 'HR Year to Date Config'
    
    name = fields.Char('Name', required=True)
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'ytd_rule_ids_rel', 'ytd_rule_id', 'rule_id', 'Salary Rule', required=True)
    active = fields.Boolean('Active', default=True)


class HRAnnulizationStructure(models.Model):
    _name = 'hr.annulization_structure.config'
    _description = 'HR Annulization Structure Config'
    _order = 'sequence,id'
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)
    annulization_type = fields.Selection([('1-non-taxable', 'Non-Taxable/Exempt Compensation Income'),('2-taxable','Taxable Compensation Income'),
                             ('3-summary','Summary')], 'Type')
    computation = fields.Selection([('19','19 in BIR 2316'),('20','20 in BIR 2316'),('21','21 in BIR 2316'),('22','22 in BIR 2316'),('23','23 in BIR 2316'),
                                    ('24','24 in BIR 2316'),('25','25 in BIR 2316'),('25A','25A in BIR 2316'),('25B','25B in BIR 2316'),('26','26 in BIR 2316'),
                                    ('27','27 in BIR 2316'),('28','28 in BIR 2316'),('29','29 in BIR 2316'),('30','30 in BIR 2316'),('31','31 in BIR 2316'),
                                    ('32','32 in BIR 2316'),('33','33 in BIR 2316'),('34','34 in BIR 2316'),('35','35 in BIR 2316'),('36','36 in BIR 2316'),
                                    ('37','37 in BIR 2316'),('38','38 in BIR 2316'),('39','39 in BIR 2316'),('40','40 in BIR 2316'),('41','41 in BIR 2316'),
                                    ('42','42 in BIR 2316'),('42A','42A in BIR 2316'),('42B','42B in BIR 2316'),('43','43 in BIR 2316'),('44','44 in BIR 2316'),('45','45 in BIR 2316'),('46','46 in BIR 2316'),
                                    ('47','47 in BIR 2316'),('48','48 in BIR 2316'),('49','49 in BIR 2316'),('49A','49A in BIR 2316'),('49B','49B in BIR 2316'),('50','50 in BIR 2316')],
                                    'Item in BIR')
    sequence = fields.Integer('Sequence', default=1)
    ytd_amount = fields.Selection([('current','Current Year to Date Amount'),('previous','Previous Employer')], 'YTD Amount')
    earner_type = fields.Selection([('mmw','Minimum Wage Earner'),('nonmmw','Non Minimum Wage Earner')], 'Earner Type')
    ytd_ids = fields.Many2many('hr.year_to_date.config', 'ytd_rel', 'ytd_config_id', 'ytd_id', 'YTD')
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'annualization_rel', 'ann_id', 'rule_id', 'Salary Rules')
    condition = fields.Selection([('plus', 'Plus'), ('minus', 'Minus')], string='Condition')

    def generate_values(self,employees,date_from,date_to,report_type, domain=[]):
        annualization_list = self.env['hr.annulization_structure.config'].search(domain, order='sequence').sorted(key=lambda l:l.annulization_type)
        annulization_type = self.fields_get(allfields=['annulization_type'])['annulization_type']['selection']
        values = []
        amount = 0
        ytds = employees and self.env['hr.year_to_date'].search([('employee_id','in',employees.ids), ('ytd_date', '>=', date_from), ('ytd_date', '<=', date_to)])
        for employee in employees:
            ytd = ytds.filtered(lambda l: l.employee_id == employee)
            bir_list = []
            if ytd:
                if report_type == 'bir-2316':
                    value = {}
                    value.update({
                        'employee_id': employee,
                        'ytd': ytd,
                        'emp_addr': ",".join(filter(lambda r: r !='', [employee.street or '',
                            employee.street2 or '',
                            employee.city2 or '',
                            employee.state_id.name or '',
                            employee.country_id.name or '']))
                    })
                else:
                    value = []
                    value.append(employee.name)
                for record in annualization_list:
                    if (record.earner_type and record.earner_type == employee.contract_id.earner_type) or not record.earner_type:
                        payslips = self.env['hr.payslip'].search([('date_from','>=',date_from),
                                                                  ('date_to','<=',date_to),
                                                                  ('state','=','done'),
                                                                  ('credit_note','=',False),
                                                                  ('employee_id','=',employee.id)])
                        salary_rule = False
                        if record.salary_rule_ids:
                            salary_rule = payslips.mapped('line_ids').filtered(lambda l: l.salary_rule_id in record.salary_rule_ids)
                        if record.ytd_amount == 'current':
                            amount = sum(ytd.mapped('year_to_date_line').filtered(lambda l: l.ytd_config_id in record.ytd_ids).mapped('current_ytd_amount'))
                            if record.condition == 'minus' and salary_rule:
                                amount = amount - sum(salary_rule.mapped('total'))
                            elif record.condition == 'plus' and salary_rule:
                                amount = amount + sum(salary_rule.mapped('total'))
                        elif record.ytd_amount == 'previous':
                            amount = sum(ytd.mapped('year_to_date_line').filtered(lambda l: l.ytd_config_id in record.ytd_ids).mapped('old_ytd_amount'))
                            if record.condition == 'minus' and salary_rule:
                                amount = amount - sum(salary_rule.mapped('total'))
                            elif record.condition == 'plus' and salary_rule:
                                amount = amount + sum(salary_rule.mapped('total'))
                        else:
                            amount = sum(ytd.mapped('year_to_date_line').filtered(lambda l: l.ytd_config_id in record.ytd_ids).mapped('amount_total'))
                            if record.condition == 'minus' and salary_rule:
                                amount = amount - sum(salary_rule.mapped('total'))
                            elif record.condition == 'plus' and salary_rule:
                                amount = amount + sum(salary_rule.mapped('total'))
                    else:
                        amount = 0
                    if report_type == 'bir-2316':
                        if value.get(record.computation):
                            value.update({str(record.computation): amount + value[str(record.computation)]})
                        else:
                            value.update({str(record.computation):amount})
                        if record.computation in ['42A','42B','49A','49B']:
                            value.update({str(record.computation) + '-text':record.name})
                    elif report_type == 'annualization-report':
                        if record.computation in bir_list:
                            index = bir_list.index(record.computation)
                            val = value[index + 1]
                            value[index + 1] = val + amount
                        else:
                            bir_list.append(record.computation)
                            value.append(amount)
                values.append(value)
        return {
            'annulization_type': annulization_type,
            'annualization_list': annualization_list,
            'values':values
        }