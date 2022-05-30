from odoo import models,fields

class ProrateConfig(models.Model):
    _name = 'hr.prorate_config'
    _rec_name = 'des_name'
    
    des_name = fields.Selection([(1,'Other Non Taxable Income'),(2,'Other Taxable Income'),
                                 (3,'Withholding Tax'),(4,'Net Taxable Pay'),(5,'Total Earnings'),
                                 (6,'Final Net Pay'),(7,'Basic semi-monthly'),(8,'Basic Monthly'),
                                 (9,'GROSS'),(10,'Net Pay After Tax'),
                                 (11,'other categories with fix amount')                      
                                                                 ],string='Description',help="Computations base on salary rule")
    code = fields.Char(required=True,string='Code',help="code in payroll line")
    categ_line_ids = fields.Many2many('hr.salary.rule.category',string='Category',help="categories  base on salary rule computations")
    remarks = fields.Text(string="Remarks")