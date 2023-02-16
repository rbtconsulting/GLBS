# -*-coding:utf-8-*-
from odoo import models, fields, api


class HRLeavesType(models.Model):
    _name = 'tardiness.table'
    _description = 'Tardiness Deduction Policy'
    _rec_name = 'condition'

    condition = fields.Integer(string="Condition")
    range1 = fields.Integer(string="Range From", required=True)
    range2 = fields.Integer(string="Range To", required=True)
    equivalent_min = fields.Integer("Equivalent Mins", required=True)
    deduction_amount = fields.Float("Deduction",)
