# -*- coding:utf-8 -*-

from datetime import datetime
from odoo import api, models, fields


class ReportLeaveConversiont(models.AbstractModel):
    _name = 'report.additional_features.leave_conversion_template'

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['hr.leaves.conversion'].browse(docids)


        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.leaves.conversion',
            'data': data,
            'docs': docs,
        }

        return self.env['report'].render('additional_features.leave_conversion_template', docargs)