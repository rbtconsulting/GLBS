# -*- coding: utf-8 -*-
from odoo import models, fields,api


class AcademicExp(models.Model):
    _inherit = 'hr.curriculum'

    academic_exp = fields.Selection([('high_school','High School'),
                                     ('college','College/Bachelor'),
                                     ('master', "Master's Degree"),
                                     ('doctorate_degree', 'Doctorate Degree')],'Academic Experiences')

    @api.onchange('academic_exp')
    def onchange_academic_exp(self):
        if self.academic_exp:
            values = dict(self.fields_get(['academic_exp'])['academic_exp']['selection'])
            self.name = values[self.academic_exp]