#-*- coding:utf-8 -*-
from odoo import api, fields, models, _

class BIR1601cReportStructure(models.Model):
    _name = 'bir.1601c.report.config'
    _description = 'BIR 1601-c Report Structure'

    name = fields.Char('Name')
    code = fields.Integer('Item')
    earner_type = fields.Selection([('mmw','Minimum Wage Earner'),('nonmmw','Non Minimum Wage Earner')], 'Earner Type')
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'bir1601_report_salary_rule_rel', 'bir1601_report_config_id', 'rule_id', 'Salary Rules')
