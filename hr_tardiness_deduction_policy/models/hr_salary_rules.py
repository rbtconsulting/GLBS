from odoo import fields, models, api


class HRSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_tardiness_policy = fields.Boolean("Tardiness Policy")
