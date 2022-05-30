from odoo import models,api,fields
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta

class PayrollHDMFContribution(models.Model):
    _name = 'payroll.hdmf.contribution'
    _description = 'Pag-Ibig Contribution Table(HDMF)'
    
    @api.onchange('min_range', 'max_range')
    def onchange_range(self):
        
        if self.min_range > self.max_range and self.max_range > 0:
            self.min_range = ''
            raise UserError(_('The minimum range must be lesser than max range.'))
        
    code = fields.Char('Code', size=8, required=True, help="Code")
    name = fields.Char('Name', size=16, required=True, help="Monthly Compensation")
    min_range = fields.Float('Minimum Range', 
                             default=0, 
                             required=True, 
                             help="Minimum range of compensation.")
    max_range = fields.Float('Maximum Range',
                     default=0, required=True, help="Maximum range of compensation.")
    employee_share = fields.Float('Employee Share (%)', default=0, help="Employee Share")
    employer_share = fields.Float('Employer Share (%)' , default=0, help="Employer Share") 
    
    _sql_contraints = [('uniq_code', 'unique(code)', 'The code must be unique!')]
    
class PayrollSSSContribution(models.Model):
    _name = 'payroll.sss.contribution'
    _description = 'Social Security System Contribution Table(SSS)'
    
    @api.onchange('min_range', 'max_range')
    def onchange_range(self):
        
        if self.min_range > self.max_range and self.max_range > 0:
            self.min_range = ''
            raise UserError(_('The minimum range must be lesser than max range.'))
        
    @api.depends('ss_er', 'ss_ee', 'ec_er', 'contrib_er', 'contrib_ee')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.ss_er + record.ss_ee
            record.amount_total2 = record.contrib_er + record.contrib_ee 
    
    @api.depends('ss_ee', 'ss_er', 'ec_er','mpf_ee','mpf_er')
    def _compute_contribution(self):
        for record in self:
            record.contrib_er = record.ss_er + record.ec_er + record.mpf_er
            record.contrib_ee = record.ss_ee + record.mpf_ee
            
    code = fields.Char('Code', size=8, required=True, help="Code")
    name = fields.Char('Name', size=16, required=True, help="Monthly Compensation")
    min_range = fields.Float('Minimum Range', 
                             default=0, 
                             required=True, 
                             help="Minimum range of compensation.")
    max_range = fields.Float('Maximum Range',
                     default=0, required=True, help="Maximum range of compensation.")
    salary_credit = fields.Float('Monthly Salary Credit', 
                        default=0, required=True, help='Monthly Salary Credit.')
    ss_er = fields.Float("SS(ER)", default=0, required=True, help="Social Security(Employer)")
    ss_ee = fields.Float("SS(EE)", default=0, required=True, help="Social Security(Employee)")
    amount_total = fields.Float('Amount Total', 
                compute='_compute_amount_total', 
                default=0, store=True, help="Amount Total(SS)")
    mandatory_fund = fields.Float(string="Mandatory Provident Fund")
    effectivity_start = fields.Date(string='Start')
    effectivity_end = fields.Date(string='End')
    mpf_ee = fields.Float("MPF (EE)")
    mpf_er = fields.Float("MPF (ER)")
    dummy_end_date = fields.Date(store=True,compute='get_end_date')


    @api.depends('effectivity_start','code','effectivity_end')
    def get_end_date(self):
        for item in self:
            if not item.effectivity_end:
                item.dummy_end_date = date.today() + relativedelta(years=10)
            else:
                item.dummy_end_date = item.effectivity_end
    
    ec_er = fields.Float("EC(ER)", 
                default=0, 
                required=True, 
                help="EC(Employer)")
    
    contrib_er = fields.Float("Contribution(ER)",
                default=0, 
                compute="_compute_contribution", 
                required=True, 
                store=True,
                help="Contribution(Employer)")
    
    contrib_ee = fields.Float("Contribution(EE)", 
                default=0, 
                compute="_compute_contribution", 
                required=True,
                store=True, 
                help="Contribution(Employee)")
    
    amount_total2 = fields.Float('Total Contribution', 
                compute='_compute_amount_total', 
                default=0, 
                store=True, 
                help="Total Contribution")

    _sql_contraints = [('uniq_code', 'unique(code)', 'The code must be unique!')]
    
    
class PayrollPHICContribution(models.Model):
    _name = 'payroll.phic.contribution'
    _description = 'Philhealth Insurance Corporation Contribution(PHIC)'
    
    @api.onchange('min_range', 'max_range')
    def onchange_range(self):
        
        if self.min_range > self.max_range and self.max_range > 0:
            self.min_range = ''
            raise UserError(_('The minimum range must be lesser than max range.'))
        
    @api.depends('personal_share', 'employer_share')
    def _compute_monthly_premium(self):
        for record in self:
            record.monthly_premium = record.personal_share + record.employer_share
            
    code = fields.Char('Code', size=8, required=True, help="Code")
    name = fields.Char('Name', size=16, required=True, help="Monthly Basic Salary")
    min_range = fields.Float('Minimum Range',   
                             default=0, 
                             required=True, 
                             help="Minimum range of basic salary.")
    max_range = fields.Float('Maximum Range',
                     default=0, required=True, help="Maximum range of basic salary.")
    
    monthly_premium = fields.Float("Monthly Premium", 
                        compute="_compute_monthly_premium", 
                        default=0, store=True, help="Monthly Premium")
    personal_share = fields.Float("Personal Share", default=0, required=True, help="Personal Shares")
    employer_share = fields.Float("Employer Share", default=0, required=True, help="Employer Share")


class PayrollWithholdingTaxContribution(models.Model):
    _name = 'payroll.withholding_tax.contribution'
    _description = 'Withholding Tax Contribution Table'
    
    @api.onchange('min_range', 'max_range')
    def onchange_range(self):
        
        if self.min_range > self.max_range and self.max_range > 0:
            self.min_range = ''
            raise UserError(_('The minimum range must be lesser than max range.'))
        
    code = fields.Char('Code', size=8, required=True, help="Code")
    name = fields.Char('Name', size=16, required=True, help="Compensation")
    min_range = fields.Float('Minimum Range', 
                             default=0, 
                             required=True, 
                             help="Minimum range of compensation.")
    max_range = fields.Float('Maximum Range',
                     default=0, required=True, help="Maximum range of compensation.")
   
   
    compensation_level = fields.Selection([('1', '1'), 
                                           ('2', '2'), 
                                           ('3', '3'),
                                           ('4', '4'), 
                                           ('5', '5'), 
                                           ('6', '6')], 'Compensation Level', required=True)
    contrib_method = fields.Selection([('daily', 'Daily'), 
                               ('weekly', 'Weekly'),
                               ('semi_monthly', 'Semi-Monthly'),
                               ('monthly', 'Monthly')], 'Method of Contribution', required=True)
    
    percentage = fields.Float('Percentage(%) over CL', required=True)
    prescribed_tax = fields.Float('Prescribed Minimum Withholding Tax', required=True)
   
    _sql_contraints = [('uniq_code', 'unique(code)', 'The code must be unique!')]

class AnnualIncomeTax(models.Model):
    _name = 'annual.income.tax'
    _description = 'Annual Income Tax Table'
    
    name = fields.Char('Tax Base', required=True)
    min_range = fields.Float('Minimum Range', 
                             default=0, 
                             required=True, 
                             help="Minimum range of Annual Income")
    max_range = fields.Float('Maximum Range',
                     default=0, required=True, help="Maximum range of Annual Income")
    
    percentage = fields.Float('Percentage(%)', required=True)
    prescribed_tax = fields.Float('Fixed Annual Income Tax', required=True)
   
class AlphanumericTaxCode(models.Model):
    _name = 'alphanumeric.tax.code'
    _description = 'Alphanumeric Tax Code'
    
    def get_rate(self, code, atc_type):
        """Returns atc value."""
        return self.search([('code', '=', code), ('atc_type', '=', atc_type)])
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.code))
        return  res
    
    code = fields.Char('ATC', required=True, help="Alphanumeric Tax Codes")
    atc_type = fields.Selection([('ind', 'Individual'), ('corp', 'Corporate')], 'ATC Type', required=True)
    tax_rate = fields.Float('Tax Rate', required=True)
    description = fields.Text('Description', required=True)
