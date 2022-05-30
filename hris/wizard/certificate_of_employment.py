from odoo import fields, models, api

class CertificateEmployment(models.TransientModel):
    _name = "employee.coe"
    _description = "Certificate of Employment"

    select_template = [('1', 'COE Template 1'),
                       ('2', 'COE Template 2')]

    @api.onchange('employee_id', 'state')
    def onchange_status(self):
        if self.employee_id:
            contract_id = self.employee_id.contract_id
            self.date_from = contract_id.date_start
            
            if contract_id and not contract_id.resigned:
                self.state = 'employed'
            
            if contract_id and contract_id.resigned:
                self.state = 'resigned'
            
            if self.state == 'employed':
                self.date_to = fields.Date.context_today(self)
            
            if self.state == 'resigned' and contract_id.resigned:
                self.date_to = contract_id.date_end
                
            if self.employee_id.parent_id:
                self.approved_by = self.employee_id.parent_id.id
                
    date_from = fields.Date(string='Hired Date', required=True)
    date_to = fields.Date(string='End Date', default=lambda s:fields.Date.context_today(s))
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    state = fields.Selection([('employed','Employed'), ('resigned', 'Resigned')], 'Status', default="employed", readonly=True)
    #employee_ids = fields.Many2many('hr.employee', 'emp_coe_rel', 'emp_coe_id', 'employee_id', string='Employees', required=True)
    approved_by = fields.Many2one('hr.employee', string='Approved By', required=True)
    purpose = fields.Text(required=True)
    temp_select = fields.Selection(select_template, string="Select Template", default='1')

    @api.multi
    def print_report(self):
        self.ensure_one()

#         data = {'ids': self.ids}
        res = self.read()
        res = res and res[0] or {}
        
        data = {'form': res}
        if self.temp_select == '1':
            return self.env['report'].get_action(self, 'hris.report_employee_coe_template1', data=data)
        elif self.temp_select == '2':
            return self.env['report'].get_action(self, 'hris.report_employee_coe_template2', data=data)
        else:
            raise ValidationError("Template doesn't exist.")

