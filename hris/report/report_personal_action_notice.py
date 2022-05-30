# -*- coding:utf-8 -*-
from odoo import api, models

class ReportPersonalActionNotice(models.AbstractModel):
    _name = 'report.hris.report_personal_action_notice'

    def get_general_info(self, form):
        emp_id = form.get('emp_no')
        emp = self.env['hr.employee'].search([('barcode', '=', emp_id)])
        
        if emp:
            contract = emp.contract_id
            
            for details in emp:
                #address = details.street + details.street2,details.city2,details.state_id.name,details.zip 
                d = {
                     'EMP_NO' : emp_id,
                     'FN' : details.firstname or '',
                     'LN' : details.lastname or '',
                     'MN' : details.middlename or '',
                     'ST_1' : details.street or '',
                     'ST_2' : details.street2 or '',
                     'CITY' : details.city2 or '',
                     'STATE' : details.state_id.name or '',
                     'STATUS' : details.marital or '',
                     'GENDER' : details.gender or '',
                     'DATE_HIRED' : contract.date_start or '',
                     'DATE_REG' : contract.date_permanent or '',
                     'SSS' : details.sss_no or '',
                     'TIN' : details.identification_id or '',
                     'PHIC' : details.phic_no or '',
                     }
                return d
                
    def get_typ_action_details(self,form):
          
        hiring =  form.get('hiring',None)
        sal_changes = form.get('salary_changes',None)
        pos_changes = form.get('pos_changes',None)
        leave_abs = form.get('leave_abs',None)
        separation = form.get('separation',None)
        
        d = {  
          'HIRING' : hiring,
          'SAL_CHANGES' : sal_changes,
          'POS_CHANGES' : pos_changes,
          'LEAVE_ABS' : leave_abs,
          'SEPARATION' : separation,
            }   
        return d
    
    def get_item_des_details(self, form):
        emp_no = form.get('emp_no', None)
        emp = self.env['hr.employee'].search([('barcode', '=', emp_no)])
        contract = emp.contract_id
        emps = emp.department_id.name
        posi = emp.job_id.name
        dep = form.get('dep', None) and form.get('dep', None)[1]
        pos = form.get('pos', None) and form.get('pos', None)[1]
        lvl = form.get('level', None) or ''
        rep_to = form.get('rep_to', None) and form.get('rep_to', None)[1]
        emp_typ = form.get('emp_typ', None) and form.get('emp_typ', None)[1]
        remarks = form.get('remarks', None) or ''
        con_emp_typ = contract.type_id.name
        
        basic_sal = contract.wage
        tot_deminimis = 0.0
        tot_other_all = 0.0
        for ded in contract:
            if ded.other_deduction_line:
                for val in ded.other_deduction_line:
                    tot_deminimis += val.amount
            if ded.other_income_line:
                for val in ded.other_income_line:
                    tot_other_all += val.amount
        total_gorss = basic_sal + tot_other_all - tot_deminimis
        
        details = {}
        details['DEPARTMENT'] = dep
        details['POSITION'] = pos
        details['LEVEL'] = lvl
        details['REP_TO'] = rep_to
        details['EMP_TYP'] = emp_typ
        details['BASIC'] = basic_sal
        details['DEMINIMIS'] = tot_deminimis
        details['ALLOWANCE'] = tot_other_all
        details['GROSS'] = total_gorss
        details['REMARKS'] = remarks
    
        return details
    
    def get_other_details(self, form):
        effectivity_date = form.get('efectivity_date') or ''
        rev_no = form.get('revision_no') or ''
        prep_by = form.get('prep_by')[1]
        rev_by = form.get('rev_by')[1]
        app_by = form.get('app_by')[1]
        
        details = {}
        details['EFF_DATE'] = effectivity_date
        details['REV_NO'] = rev_no
        details['PREP_BY'] = prep_by
        details['REV_BY'] = rev_by
        details['APP_BY'] = app_by
    
        return details
    
    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env['hr.personal_action_notice'].browse(self.env.context.get('active_ids'))
        
        get_general_information = self.get_general_info(data['form'])
        get_other_details = self.get_other_details(data['form']) 
        get_action_details = self.get_typ_action_details(data['form'])
        get_item_des_details =  self.get_item_des_details(data['form'])
        
        position_prep = data['prepared_by']
        position_rev = data['revised_by']
        position_app = data['approved_by']
        
        positions = {
            'PREPARED' : position_prep,
            'REVISED' : position_rev,
            'APPROVED' : position_app
        }
        
        docargs = {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'gen_info' : get_general_information,
            #'action_details' : get_action_details,
            'other_det' : get_other_details,
            'item_des' : get_item_des_details,
            'positions' : positions
        }
        
        
        return self.env['report'].render('hris.report_personal_action_notice_template', docargs)