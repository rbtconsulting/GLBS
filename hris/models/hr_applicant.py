from odoo import fields, models, api

from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class HRApplicant(models.Model):
    _inherit = 'hr.applicant'
    _rec_name = 'partner_name'


    def website_form_input_filter(self, request, values):
        
        fullname = ''
        if 'firstname' in values:
            fullname += values['firstname']
            
        if 'lastname' in values:
            fullname += " " + values['lastname']
        
        if 'middlename' in values:
            fullname += " " + values['middlename']
        
        values['partner_name'] = fullname
        
        if 'is_agree' not in values:
            values['is_agree'] = False
     
        if 'partner_name' in values:
            values.setdefault('name', '%s\'s Application' % values['partner_name'])
       
        return values
 
    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                if not applicant.employee_number:
                    raise ValidationError(_("Please first enter Employee Number!!"))
                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                               'firstname': applicant.firstname,
                                               'lastname': applicant.lastname,
                                               'middlename': applicant.middlename,
                                               'employee_num': applicant.employee_number,
                                               'job_id': applicant.job_id.id,
                                               'address_home_id': address_id,
                                               'department_id': applicant.department_id.id or False,
                                               'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                               'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                               'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        self.active = False
        return dict_act_window
    
    @api.onchange('firstname','lastname','middlename')
    def onchange_fullname(self):
        firstname = self.firstname or ''
        lastname = self.lastname or ''
        middlename = self.middlename or ''
        
        
        if middlename:
            self.partner_name = "{} {} {}".format(firstname, middlename, lastname)
        else:
            self.partner_name = "{} {}".format(firstname, lastname)
    
    firstname = fields.Char('First Name', size=16, required=True)
    lastname = fields.Char('Surname', size=16, required=True)
    middlename = fields.Char('Middle Name', size=16)
    employee_number = fields.Char('Employee Number')

    def action_view_job_offer(self):
        """Returns view job offer"""

        for record in self:
            applicant_id = self.env['hr.job_offer'].search([('applicant_id', '=', record.id)])
            vals = {
                'name'      : _('Job Offer'),
                'type'      : 'ir.actions.act_window',
                'res_model' : 'hr.job_offer',
                'view_type' : 'form',
                'view_mode' : 'form',
                'target'    : 'current'
                }
        
            if applicant_id:
                vals.update({
                    'res_id'    : applicant_id.id,
                '    view_id'   : self.env.ref('hris.hr_job_offer_view').id,
                    })
            else:
                
                vals.update({'context': {
                    'default_applicant_id': record.id,
                    'default_position_id':  record.job_id.id,
                    'default_department_id': record.department_id.id,
                    'default_employers_id': record.company_id.id
                    }
                })
            
            return vals
