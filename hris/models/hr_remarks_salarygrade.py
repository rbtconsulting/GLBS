from odoo import fields,models,api

class HRRemarksSalaryGrade(models.Model):
    _name = 'hr.remarks.salary.grade'
    
    name = fields.Char('Salary Grade Remarks')
