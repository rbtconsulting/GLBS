from odoo import models,fields,api
from datetime import datetime

class JobOffer(models.Model):
    _name = 'hr.job_offer'
    _description = 'Job Offer For Applicants'
    _rec_name = 'applicant_id'
    
    applicant_id = fields.Many2one('hr.applicant', string="Applicant name", required=True)
    position_id = fields.Many2one('hr.job', string="Position")
    department_id = fields.Many2one('hr.department', string="Department/Section")
    immediate_superior = fields.Many2one('hr.employee', string="Immediate Supervisor", required=True)
    interface_with = fields.Char(string="Interface With")
    employers_id = fields.Many2one('res.company', string="Employer's Name")
    job_location = fields.Many2one('hr.employee.work_location', string="Job Location")
    work_schedule = fields.Char(string="Work Schedule")
    effectivity_date = fields.Date(string="Effectivity Date")
    prepared_by_id = fields.Many2one('hr.employee', string="Prepared by", required=True)
    endorsed_by_id = fields.Many2one('hr.employee', string="Endorsed by", required=True)
    approved_by_id = fields.Many2one('hr.employee', string="Approved by", required=True)
    hr_compensation_ids = fields.One2many('hr.compensation_others','job_offer_id')
    hr_perks_ids = fields.One2many('hr.other_perks_and_benefits','job_offer_id')

    @api.multi
    def btn_job_offer(self):
        
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', []),
                'prepared_by' : self.prepared_by_id.job_id.name,
                'endorsed_by' : self.endorsed_by_id.job_id.name,
                'approved_by' : self.approved_by_id.job_id.name                
                }
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        
        return self.env['report'].get_action(self,'hris.report_job_offer', data=data)
    
class CompensationOthers(models.Model):
    _name = 'hr.compensation_others'
    _description = 'Compensation and Others'
    
    compensation_others = fields.Char(string="Compensation and Others")
    amount = fields.Float(string="Amount")
    remarks = fields.Char(string="Remarks")
    job_offer_id = fields.Many2one('hr.job_offer')
    
class OtherPerksbenefits(models.Model):
    _name = 'hr.other_perks_and_benefits'
    _description = 'Other Perks and Benefits'
    
    perks_benefits = fields.Char(string="Other Perks And Benefits")
    description = fields.Char(string="Description")
    job_offer_id = fields.Many2one('hr.job_offer')