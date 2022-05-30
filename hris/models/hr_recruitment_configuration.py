# -*- coding: utf-8 -*-
from odoo import models, fields

class HRConfigSettings(models.TransientModel):
    _inherit = 'hr.recruitment.config.settings'


    module_hr_recruitment_survey = fields.Selection(selection=[
        (0, "Do not use application forms"),
        (1, "Use application forms during the recruitment process")
        ], string='Application Form')