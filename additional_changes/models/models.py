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
    