from odoo.exceptions import ValidationError

from odoo import fields, models, api


class ModifyMackun(models.Model):
    _inherit = 'hr.payslip'


    id_company = fields.Many2one(related="employee_id.id_company",string="Company", readonly="1")