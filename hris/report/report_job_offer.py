# -*- coding:utf-8 -*-

from datetime import datetime, date
from datetime import timedelta
from odoo import api, models


class ReportJobOffer(models.AbstractModel):
    _name = 'report.hris.report_job_offer'
    
    def get_job_offer_form_details(self, form):
        
        compensation_ids = form.get('hr_compensation_ids')
        perk_ids = form.get('hr_perks_ids')
        compensation = self.env['hr.compensation_others'].browse(compensation_ids)
        perks = self.env['hr.other_perks_and_benefits'].browse(perk_ids)
        
        applicant_details = []
        for records in compensation:
            d = {}
            compensation_others = records.compensation_others
            amount = records.amount
            remarks = records.remarks
            
            d.update({
                'COMPENSATION'  :compensation_others,
                'AMOUNT' : amount,
                'REMARKS' : remarks
            })  
            applicant_details.append(d)
       
        return applicant_details
    
    def get_perk_details(self,form):
        perk_ids = form.get('hr_perks_ids')
        perks = self.env['hr.other_perks_and_benefits'].browse(perk_ids)
        perk_details = []
        for rec in perks:
            e = {}
            perks_benefits = rec.perks_benefits,
            description = rec.description
            
            e.update({
                'PERKS' : perks_benefits[0],
                'DESCRIPTION' : description                
                })
            perk_details.append(e)
        
        return perk_details
    
    def get_details(self,form):
          
        effectivity_date =  form.get('effectivity_date',None)
        #date = datetime.strptime(effectivity_date, '%Y-%m-%d').strftime('%m/%d/%Y')
        applicant_name = form.get('applicant_id') and form.get('applicant_id')[1]
        position = form.get('position_id') and form.get('position_id')[1]
        department = form.get('department_id') and form.get('department_id')[1]
        superior = form.get('immediate_superior') and form.get('immediate_superior')[1]
        interface = form.get('interface_with')
        employers_name = form.get('employers_id') and form.get('employers_id')[1]
        job_location = form.get('job_location') and form.get('job_location')[1]
        work_schedule = form.get('work_schedule')
        prepared_by = form.get('prepared_by_id') and form.get('prepared_by_id')[1]
        endorsed_by = form.get('endorsed_by_id') and form.get('endorsed_by_id')[1]
        approved_by = form.get('approved_by_id') and form.get('approved_by_id')[1]
        
        d = {  
            'APPLICANT_NAME' : applicant_name or '',
            'POSITION' : position or '',
            'DEPARTMENT' :department or '',
            'SUPERIOR' : superior or '',
            'INTERFACE' : interface or '',
            'EMP_NAME' : employers_name or '',
            'JOB_LOC' : job_location or '',
            'WORK_SCHED' : work_schedule or '',
            'DATE' : effectivity_date or '',    
            'PREPARED' : prepared_by or '',
            'ENDORSED' : endorsed_by or '',
            'APPROVED' : approved_by or '',
            }   
        return d
    
    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_job_offer_form_details = self.get_job_offer_form_details(data['form'])
        get_details = self.get_details(data['form']) 
        get_perk_details = self.get_perk_details(data['form'])
        position_prep = (data['prepared_by'])
        position_end = (data['endorsed_by'])
        position_app = (data['approved_by'])
        
        positions = {
            'PREPARED' : position_prep,
            'ENDORSED' : position_end,
            'APPROVED' : position_app
            }
        
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'details'   : get_details,
            'job_offer' : get_job_offer_form_details,
            'perks' : get_perk_details,
            'positions' : positions
        }
        return self.env['report'].render('hris.report_job_offer_template', docargs)