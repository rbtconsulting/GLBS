# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import math

class DisciplinaryActions(models.Model):
    _name = 'hr.disciplinary'
    _description = "Disciplinary Actions"
    _rec_name = 'employee_id'

    @api.onchange('penalty_id')
    def onchange_penalty_id(self):
        if self.penalty_id:
            values = dict(self.fields_get(['penalty_id'])['penalty_id']['selection'])
            self.case_id = values[self.penalty_id]

    @api.constrains('start_date', 'end_date')
    def check_change(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError(_('"End date" is greater than "Start date" date.'))

    @api.depends('start_date', 'end_date')
    def _compute_total_days(self):
        for record in self:
            if record.start_date and record.end_date:
                start_date = fields.Datetime.context_timestamp(record, fields.Datetime.from_string(
                    record.start_date))
                end_date = fields.Datetime.context_timestamp(record,
                                                             fields.Datetime.from_string(record.end_date))
                time_delta = (end_date - start_date)
                record.diff_days =  math.ceil((time_delta.days)  + float(time_delta.seconds) / 86400)
               
                record.diff_days = record.diff_days + ' ' + 'day(s)'
    
    def get_employee_attendance(self):
        """Return employee attendances that matched on the approved leaves."""
        attendance = self.env['hr.attendance']
        for record in self:
            """
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('schedule_in', '>=', record.date_from),
                ('schedule_out','<=', record.date_to),
                ]
            attendance |= self.env['hr.attendance'].search(domain)
            """
            domain2 = [
                ('employee_id', '=', record.employee_id.id),
                ('schedule_in', '<=', record.end_date),
                ('schedule_out','>=', record.start_date),
                ]
            
            attendance |= self.env['hr.attendance'].search(domain2)
            
        return attendance
    
    def apply_to_attendance(self):
        """Apply specific disciplinary action to employee."""
        attendances = self.get_employee_attendance()
        
        for attendance in attendances:
            attendance. write({'remarks': 'SUS', 'is_suspended': True})

    def apply_suspension(self):
        if self.penalty_id == 'suspension':
            self.apply_to_attendance()
        if self.penalty_id == 'dismissal':
            self.employee_id.terminate()
            
    @api.model
    def create(self, vals):
        res = super(DisciplinaryActions, self).create(vals)
        self.apply_suspension()
        return res
    
    @api.multi
    def write(self, vals):
        res = super(DisciplinaryActions, self).write(vals)
        self.apply_suspension()
        return res
    
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    diff_days = fields.Char(string='Duration', compute="_compute_total_days", store=True)
    case_id = fields.Char('Name of Case', required=True)
    occurence_date = fields.Date('Occurence Date', required=True)
    penalty_id = fields.Selection([('verbal written', 'Verbal'),
                                   ('written', 'Written Warning'),
                                   ('suspension', 'Suspension'),
                                   ('final_written','Final Written Warning'),
                                   ('dismissal', "Dismissal")], 'Penalty', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    effect_date = fields.Date('Effectivity Date', required=True)
    recommended_by_id = fields.Many2one('hr.employee',string="Recommended By")

class HrEmployees(models.Model):
    _inherit = 'hr.employee'

    disciplinary_ids = fields.One2many('hr.disciplinary', 'employee_id', 'Disciplinary Action')

