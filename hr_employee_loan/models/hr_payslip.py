# -*- coding: utf-8 -*-

from odoo import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for rec in self:
            all_install_ids = self.env['loan.installment.details'].search([('employee_id','=',rec.employee_id.id)])
#             install_ids = self.env['loan.installment.details'].search([('employee_id','=',rec.employee_id.id),
#                                                                        ('date_from','>=',rec.date_from),
#                                                                        ('date_from','<=',rec.date_to)
#                                                                        ])
            line = rec.line_ids.filtered(lambda l:l.salary_rule_id.is_loan_payment)
            line_salary = rec.line_ids.mapped('salary_rule_id').ids
            install_ids = all_install_ids.filtered(lambda l: any(id in l.loan_type.mapped('salary_rule_ids').ids for id in line_salary) and 
                                        (l.date_from >= rec.date_from and l.date_from <= rec.date_to) or 
                                        (l.date_to > rec.date_from and l.date_to <= rec.date_to) or 
                                        (l.date_to > rec.date_to and l.date_from <= rec.date_from))
#             install = install_ids.filtered(lambda l: any(id in l.loan_type.mapped('salary_rule_ids').ids for id in line_salary))
            paid_amount = 0
            for rec in line:
                paid_amount += rec.amount
            if line or install_ids:
                for install in install_ids:
                    install.paid_amount += paid_amount
                    install.pay_installment()
        return res

#     @api.model
#     def get_loan_installment(self, emp_id, date_from, date_to=None):
#             self._cr.execute("SELECT o.id, o.install_no from loan_installment_details as o where \
#                                 o.employee_id=%s \
#                                 AND to_char(o.date_from, 'YYYY-MM-DD') >= %s AND to_char(o.date_from, 'YYYY-MM-DD') <= %s ",
#                                 (emp_id, date_from, date_to))
#             res = self._cr.dictfetchall()
#             install_ids = []
#             if res:
#                 install_ids = [r['id']for r in res]
#             return install_ids
