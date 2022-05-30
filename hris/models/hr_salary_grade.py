from odoo import fields,models,api

class HRSalaryGrade(models.Model):
    _name = 'hr.salary.grade'
    _rec_name = 'salary_grade'
    _order = 'salary_grade ASC'
    
    salary_grade = fields.Many2one('hr.salary.grade.name')
    sg_step = fields.Many2one('hr.salary.step.name')
    sg_amount = fields.Float('Amount')
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = 'Sg' + str(record.salary_grade) + 'Step' + str(record.sg_step)
            res.append((record.id, name))
        return  res
    
class HRGradeName(models.Model):
    _name = 'hr.salary.grade.name'
    
    name = fields.Char('name')

class HRStepname(models.Model):
    _name = 'hr.salary.step.name'
    
    name = fields.Char('name')     
     
#class HRjobpositionsalarygrade(models.Model):
#    _inherit = 'hr.job'
#    
#    salary_grade = fields.Many2one('hr.salary.grade.name')
