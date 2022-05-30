
from datetime import datetime
from odoo import models, fields, api, SUPERUSER_ID
from lxml import etree
import json
from odoo.osv.orm import setup_modifiers

class JobOfferWizard(models.TransientModel):
    _name = "hr.job.offer"
    _description = "job offer Wizard"


    def _get_default_start_date(self):
            year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
            return '{}-01-01'.format(year)

    def _get_default_end_date(self):
            date = fields.Date.from_string(fields.Date.today())
            return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')


    #date_from = fields.Date(string='Start Date', required=True, default=_get_default_end_date)
    employee_id = fields.Many2one('hr.employee' ,string="Employee",required=True)
    job_id = fields.Many2one('hr.job', string='Position',required=True)
    department_id = fields.Many2one('hr.department', string='Department',required=True)
    superior = fields.Many2one('hr.employee' ,string="Immediate Superior",required=True)
    interface_with = fields.Char(string="Interface With")
    company_id = fields.Many2one('res.company', string="Employer's  Name",required=True)
    work_loc = fields.Char(string="Job Location")
    work_sched = fields.Char(string="Work Schedule")
    effect_date = fields.Date(string='Effectivity Date', default=_get_default_end_date)
    compensation_ids = fields.One2many('hr.job.offer.compensation', 'job_offer_id', 'COMPENSATION AND OTHERS')


    @api.multi
    def print_report(self):

        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env['report'].get_action(self, 'hris.report_job_offer_template', data=data)



class HrjobOfferExtend(models.TransientModel):
    _name = 'hr.job.offer.compensation'

    job_offer_id = fields.Char(invisible=True)
    name = fields.Char(string="Name")
    amount = fields.Char(string="Amount")
    remarks = fields.Char(string="Remarks")

