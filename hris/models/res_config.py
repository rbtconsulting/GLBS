#-*- coding-utf-8 -*-

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = 'res.partner'

    signup_token = fields.Char(groups="base.group_user")
    signup_type = fields.Char(groups="base.group_user")
    signup_expiration = fields.Datetime(groups="base.group_user")


class HrPayrollConfigSettings(models.TransientModel):
    _inherit = 'hr.payroll.config.settings'
    
    @api.multi
    def set_params(self):
        self.ensure_one()
        
        self.env['ir.config_parameter'].set_param('net.cap.percentage', repr(self.percentage))
        self.env['ir.config_parameter'].set_param('net.cap.enable', repr(self.netcap))
        self.env['ir.config_parameter'].set_param('non.tax.limit', repr(self.nontaxable_limit))
    
    @api.model
    def get_default_params(self, fields):
        res = {}
    
        res['percentage'] = float(self.env['ir.config_parameter'].get_param('net.cap.percentage', default=0))
        res['netcap'] = safe_eval(self.env['ir.config_parameter'].get_param('net.cap.enable', 'False'))
        res['nontaxable_limit'] = float(self.env['ir.config_parameter'].get_param('non.tax.limit', default=90000))
        
        return res
    
    netcap = fields.Boolean('Enable Net Cap', help="Enable minimum take home pay checking.")
    percentage = fields.Float('Percentage')
    nontaxable_limit = fields.Float('Non Taxable Limit')
    
class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'
    
    @api.multi
    def set_params(self):
        self.ensure_one()
        self.env['ir.config_parameter'].set_param('minimum.overtime.hours', repr(self.minimum_overtime_hours))
        self.env['ir.config_parameter'].set_param('default.ot.lockout', repr(self.default_ot_lockout))
        self.env['ir.config_parameter'].set_param('default.ot.lockout.period', repr(self.default_ot_lockout_period))
        self.env['ir.config_parameter'].set_param('default.ob.lockout', repr(self.default_ob_lockout))
        self.env['ir.config_parameter'].set_param('default.ob.lockout.period', repr(self.default_ob_lockout_period))

    @api.model
    def get_default_params(self, fields):
        res = {}
        # res['minimum_overtime_hours'] = float(self.env['ir.config_parameter'].get_param('minimum.overtime.hours', '1'))
        res['minimum_overtime_hours'] = float(self.env['ir.config_parameter'].get_param('minimum.overtime.hours',default=1))
        res['default_ot_lockout'] = self.env['ir.config_parameter'].get_param('default.ot.lockout', False)
        res['default_ot_lockout_period'] = float(self.env['ir.config_parameter'].get_param('default.ot.lockout.period', 0))
        res['default_ob_lockout'] = self.env['ir.config_parameter'].get_param('default.ob.lockout', False)
        res['default_ob_lockout_period'] = float(self.env['ir.config_parameter'].get_param('default.ob.lockout.period', 0))
        return res

    default_ot_lockout = fields.Boolean('Overtime Lockout', help="Enables locking out period of overtime.", default_model='hr.attendance.overtime')
    default_ot_lockout_period = fields.Float('Lockout Period', help="Lock out period(e.g. 2 payroll cut-offs)",default_model='hr.attendance.overtime')
    
    default_ob_lockout = fields.Boolean('Official Business Lockout', help="Enables locking out period of change of attendance requests.", default_model='hr.attendance.change')
    default_ob_lockout_period = fields.Float('Lockout Period', help="Lock out period(e.g. 2 payroll cut-offs)",default_model='hr.attendance.change')
    default_no_ot_late = fields.Boolean('Void overtime on tardiness', help="Employees with tardiness on the same day of requested overtime shall be void.",default_model='hr.attendance.overtime')
    minimum_overtime_hours = fields.Float('Minimum Overtime Hours', help="Minimum Overtime Hours")

class HrAttendanceSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_hr_multi_location = fields.Boolean(string='Enable multiple location ',
        help="Install hr multi location module")


class HRContractSettings(models.TransientModel):
    _inherit = 'hr.settings'

    @api.multi
    def set_params(self):
        self.ensure_one()
        
        lockout = getattr(self, 'sm_lockout', 'False')
        period = getattr(self, 'sm_lockout_period', '0') or ''
        start_at = getattr(self, 'start_at', '0')
        en_notif = getattr(self, 'enable_first', 'False')
        notif = getattr(self, 'first_notif', '0') or ''
        en_notif2 = getattr(self, 'enable_second', 'False')
        notif2 = getattr(self, 'second_notif', '0') or ''
        
        self.env['ir.config_parameter'].set_param('salary.movement.lockout', lockout)
        self.env['ir.config_parameter'].set_param('salary.movement.period', period)
        self.env['ir.config_parameter'].set_param('barcode.start', start_at)
        
        self.env['ir.config_parameter'].set_param('en.notif.days', en_notif)
        self.env['ir.config_parameter'].set_param('reg.notif.days', notif)
        
        self.env['ir.config_parameter'].set_param('en.notif2.days', en_notif2)
        self.env['ir.config_parameter'].set_param('reg.notif2.days', notif2)
        
        auto_generate = getattr(self, 'default_auto_generate_barcode', 'False')
        
        if auto_generate:
            sequence_id = self.env.ref('hris.seq_emp_id')
            sequence_id.write({'number_next_actual': start_at})
        
    def get_default_params(self, fields):
        res = {}
        res['sm_lockout'] = self.env['ir.config_parameter'].get_param('salary.movement.lockout', 'False')
        res['sm_lockout_period'] = float(self.env['ir.config_parameter'].get_param('salary.movement.period', '0'))
        res['start_at'] = self.env.ref('hris.seq_emp_id').number_next_actual
        
        res['enable_first'] = self.env['ir.config_parameter'].get_param('en.notif.days', 'False')
        res['first_notif'] = float(self.env['ir.config_parameter'].get_param('reg.notif.days', 30))
        res['enable_second'] = self.env['ir.config_parameter'].get_param('en.notif2.days', 'False')
        res['second_notif'] = float(self.env['ir.config_parameter'].get_param('reg.notif2.days', 180))
        
        return res
    
    sm_lockout = fields.Boolean('Salary Movement Lockout', help="Enables locking out period of salary movement")
    sm_lockout_period = fields.Float('Salary Movement Lockout Period', help="Lock out period(e.g. 2 payroll cut-offs)")
    
    default_auto_generate_barcode = fields.Boolean('Automatically Generate Employee Barcode', default_model="hr.employee")
    start_at = fields.Char('Start At')
    
    enable_first = fields.Boolean('Enable Second')
    first_notif = fields.Float('First Notification on Performance Review')
    
    enable_second = fields.Boolean('Enable Second')
    second_notif = fields.Float('Second Notification on Performance Review')