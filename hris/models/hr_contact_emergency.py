from odoo import fields,models,api
from datetime import datetime
from odoo.fields import One2many
from odoo.fields import Many2one

class HREmergency(models.Model):
    _inherit ="hr.employee"
    
    e_contact_ids = One2many('hr.emergency_contacts', 'employee_id', 'Emergency Contacts')
   
class HREmergencyContacts(models.Model):
    _name = 'hr.emergency_contacts'
    
    employee_id = Many2one('hr.employee', 'Employee')
    name = fields.Char('Name', size=16)
    job_position = fields.Char('Job Position', size=16)
    phone = fields.Char('Phone', size=16)
    mobile = fields.Char('Mobile', size=16)
    email = fields.Char('Email', size=16)