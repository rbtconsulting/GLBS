from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import ValidationError,UserError
from odoo.tools.translate import _
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta


class GetEmployees(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def action_approve(self):
        # raise ValidationError(self.id)
        y = self.env['hr.attendance'].create({
            'employee_id' : self.employee_id.id,
            'check_in' : self.date_from,
            'check_out': self.date_to,
        })
    
        y.write({'leave_ids': [(4, self.id)]})

        x =  super(GetEmployees, self).action_approve()
        return x

class AdditionalTables(models.Model):
    _inherit = 'payroll.sss.contribution'

    wsip_er = fields.Float(string="WSIP ER")
    wsip_ee = fields.Float(string="WSIP EE")


class PhicAdditional(models.Model):    
    _inherit = 'hr.contract'

    def get_prev_regwrk(self, contract, payslip):
        domain = [('date_release', '<', payslip.date_release),
                    ('contract_id', '=', contract.id),
                    ('contract_id.employee_id', '=', contract.employee_id.id)]
        prev_payslip = self.env['hr.payslip'].search(domain, limit=1, order="date_release DESC")
        if prev_payslip:
            datas = {'RegWrk': 0.0}
            for line in prev_payslip.line_ids:
                if line.code in datas:
                    datas[line.code] += line.total
                else:
                    continue
            total_prev_regwrk = datas['RegWrk']
            if total_prev_regwrk:
                return total_prev_regwrk
        return 0.0

    