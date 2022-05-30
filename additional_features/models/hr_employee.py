from odoo import fields, models, api


class HrEMployee(models.Model):
    _inherit ='hr.employee'

    carry_over_ids = fields.One2many('leave.carry.over','employee_id')
    carry_over_count  = fields.Float()

class CarryOver(models.Model):
    _name = 'leave.carry.over'
    _rec_name = 'amount'

    @api.depends('carry_over_line')
    def get_remaining(self):
        for record in self:
            line = record.carry_over_line.filtered(lambda x: x.leave_id and x.state_leaves == 'validate')
            total_remaining = record.original_amount -  sum(line.mapped('amount'))
            record.amount = max(0.0, total_remaining)
            record.used_amount   =  max(0.0, (record.original_amount - record.amount))

    holiday_status_id = fields.Many2one('hr.holidays.status','Holiday Type')
    prev_holiday_status_id = fields.Many2one('hr.holidays.status')
    amount = fields.Float(compute='get_remaining',string="Remaining")
    remaining_amount = fields.Float()
    used_amount = fields.Float(compute='get_remaining',string="Used")
    original_amount = fields.Float()
    employee_id = fields.Many2one('hr.employee')
    carry_over_expiration = fields.Date()
    carry_over_line = fields.One2many('leave.carry.over.line','carry_over_id',ondelete="cascade")
    year = fields.Integer()


class CarryOverline(models.Model):
    _name = 'leave.carry.over.line'
    _rec_name = 'amount'

    @api.depends('leave_id')
    def leaves_state(self):
        for record in self:
            record.state_leaves = record.leave_id.state

    carry_over_id = fields.Many2one('leave.carry.over')
    leave_id = fields.Many2one('hr.holidays')
    amount = fields.Float()
    state_leaves = fields.Char(compute='leaves_state')
    state = fields.Selection([('draft','Draft')])
    year = fields.Integer()
