from odoo import fields, models, api
from datetime import datetime,date
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from zk import ZK, const

emp_stages = [('joined', 'Newly Hired'),
              ('grounding', 'On Boarding'),
              ('test_period', 'Probationary Period'),
              ('employment', 'Start of Employment'),
              ('notice_period', 'Resignation Notice Period'),
              ('relieved', 'Resigned'),
              ('terminate', 'Terminated')]

regions = [('ncr', 'NCR'),
               ('car', 'CAR'),
               ('1', 'I'),
               ('2', 'II'),
               ('3', 'III'),
               ('4_a', 'IV-A'),
               ('4_b', 'IV-B'),
               ('5', 'V'),
               ('6', 'VI'),
               ('7', 'VII'),
               ('8', 'VIII'),
               ('9', 'IX'),
               ('10', 'X'),
               ('11', 'XI'),
               ('12', 'XII'),
               ('13', 'XIII'),
               ('armm', 'ARMM')
            ]

class EmployeeWorkLocation(models.Model):
    _name = 'hr.employee.work_location'
    _description = 'Employee Work Location'
    
    def get_region_name(self, key=''):
        """Return region name."""
        if not key:
            return ''
        regions = dict(self.fields_get(allfields=['region'])['region']['selection'])
        return regions[key]
        
    name = fields.Char('Name', required=True)
    region = fields.Selection(regions, 'Region')
    
class EmployeeStageHistory(models.Model):
    _inherit = 'hr.employee.status.history'
    
    state = fields.Selection(emp_stages, string='Stage')
      
class HREmployee(models.Model):
    _inherit ="hr.employee"
    
    """Create biometric User"""
    @api.onchange('biometric_device_id')
    def create_bio_user(self):
        if ZK:
            conn = None
            biometric_ips = self.env['hr.biometric.connection'].search([])
            if biometric_ips:
                for bio_ip in biometric_ips:
                    if bio_ip.ip_address:
                        zk = ZK(bio_ip.ip_address, port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
                     
                        try:
                            print ('Connecting to device ...')
                            conn = zk.connect()
                            emp_bio_id = self.biometric_device_id
                            
                            users = conn.get_users()
                            bio_ids = []
                            for user in users:
                                user_id = user.user_id.encode('utf-8')
                                bio_ids.append(int(user_id))
                            if emp_bio_id in bio_ids:
                                raise ValidationError(_('{} Already in Biometric'.format(emp_bio_id)))
                            else:
                                if self.name!=False:
                                    conn.set_user(uid=emp_bio_id, name=self.name, privilege=const.USER_DEFAULT, group_id='', user_id=str(emp_bio_id), card=0)
                                    conn.disconnect
                        except Exception as e:
                            print ("Process terminate : {}".format(e))
                        finally:
                            if conn:
                                conn.disconnect()
            else:
                pass

    @api.constrains('identification_id','sss_no','phic_no','hdmf_no','bank_account_id', 'bank_account_no')
    def check_employee_information(self):
        employees = self.env['hr.employee'].search([])
        for rec in self:
            if rec.identification_id and (len(employees.filtered(lambda l: l.identification_id == rec.identification_id)) > 1):
                raise ValidationError(_('You cannot create employee record with duplicate TIN number!!'))
            elif rec.sss_no and (len(employees.filtered(lambda l: l.sss_no == rec.sss_no)) > 1):
                raise ValidationError(_('You cannot create employee record with duplicate SSS number!!'))
            elif rec.phic_no and (len(employees.filtered(lambda l: l.phic_no == rec.phic_no)) > 1):
                raise ValidationError(_('You cannot create employee record with duplicate PHIC number!!'))
            elif rec.hdmf_no and (len(employees.filtered(lambda l: l.hdmf_no == rec.hdmf_no)) > 1):
                raise ValidationError(_('You cannot create employee record with duplicate HDMF number!!'))
            elif rec.bank_account_id and (len(employees.filtered(lambda l: l.bank_account_id.acc_number == rec.bank_account_id.acc_number)) > 1):
                raise ValidationError(_('You cannot create employee record with duplicate Bank Account number!!'))
            elif rec.bank_account_no and (len(employees.filtered(lambda l: l.bank_account_no == rec.bank_account_no)) > 1):
                raise ValidationError(_('You cannot create employee record with duplicate Bank Account number!!'))

    @api.model
    def _default_random_barcode(self):
        #barcode = None
        #while not barcode or self.env['hr.employee'].search([('barcode', '=', barcode)]):
        #    barcode = "".join(choice(digits) for i in range(8))
        barcode = None
        return barcode
    
    @api.model
    def create(self, vals):
            
        result = super(HREmployee, self).create(vals)
        if not result.stages_history.filtered(lambda l: l.state == 'joined'):
            result.stages_history.sudo().create({'start_date': date.today(),
                                             'employee_id': result.id,
                                             'state': 'joined'})
            
        return result

    @api.multi
    def start_grounding(self):
         
        self.state = 'grounding'
        self.stages_history.sudo().create({'start_date': date.today(),
                                           'employee_id': self.id,
                                           'state': 'grounding'})
        
    @api.multi
    def set_as_employee(self):
        self.state = 'employment'
        stage_obj = self.stages_history.search([('employee_id', '=', self.id),
                                                ('state', '=', 'test_period')])
        if stage_obj:
            stage_obj.sudo().write({'end_date': date.today()})
        self.stages_history.sudo().create({'start_date': date.today(),
                                           'employee_id': self.id,
                                           'state': 'employment'})
        
    @api.multi
    def start_notice_period(self):
        self.state = 'notice_period'
        stage_obj = self.stages_history.search([('employee_id', '=', self.id),
                                                ('state', '=', 'employment')])
        if stage_obj:
            stage_obj.sudo().write({'end_date': date.today()})
        self.stages_history.sudo().create({'start_date': date.today(),
                                           'employee_id': self.id,
                                           'state': 'notice_period'})
    
    @api.multi
    def relived(self):
        self.state = 'relieved'
        self.active = False
        stage_obj = self.stages_history.search([('employee_id', '=', self.id),
                                                ('state', '=', 'notice_period')])
        if stage_obj:
            stage_obj.sudo().write({'end_date': date.today()})
        if not self.stages_history.filtered(lambda l: l.state == 'relieved'):
            self.stages_history.sudo().create({'end_date': date.today(),
                                           'employee_id': self.id,
                                           'state': 'relieved'})
        if self.contract_id and not self.contract_id.resigned:
            self.contract_id.write({'resigned':True, 'date_end': date.today()})
        
    @api.multi
    def start_test_period(self):
        self.state = 'test_period'
        self.stages_history.search([('employee_id', '=', self.id),
                                    ('state', '=', 'grounding')]).sudo().write({'end_date': date.today()})
        self.stages_history.sudo().create({'start_date': date.today(),
                                           'employee_id': self.id,
                                           'state': 'test_period'})

    @api.multi
    def terminate(self):
        self.state = 'terminate'
        self.active = False
        stage_obj = self.stages_history.search([('employee_id', '=', self.id),
                                                ('state', '=', 'employment')])

        if stage_obj:
            stage_obj.sudo().write({'end_date': date.today()})
        else:
            self.stages_history.search([('employee_id', '=', self.id),
                                        ('state', '=', 'grounding')]).sudo().write({'end_date': date.today()})
        self.stages_history.sudo().create({'end_date': date.today(),
                                           'employee_id': self.id,
                                           'state': 'terminate'})


    @api.depends('birthday')
    def _compute_age(self):
        """Returns patient age."""
        for record in self:
            if record.birthday:
                today = datetime.today()
                age = (today - datetime.strptime(record.birthday, '%Y-%m-%d'))
                rec_age = age.days / 365.2425
                if rec_age < 18:
                    raise ValidationError(_("You are under age of 18!"))
                record.age = rec_age
    
    @api.onchange('firstname','lastname','middlename')
    def onchange_name(self):
        firstname = self.firstname or ''
        lastname = self.lastname or ''
        middlename = self.middlename or ''
        
        if middlename:
            self.name = "{} {} {}".format(firstname, middlename, lastname)
        else:
            self.name = "{} {}".format(firstname, lastname)
    
    @api.onchange('sss_no','phic_no','hdmf_no','identification_id')
    def onchange_numbers(self):
        if self.sss_no and not self.sss_no.isdigit():
            self.sss_no = ''
            return {
                  'warning': {
                  'title': _('Warning'),
                  'message': _('Invalid SSS Format')
                  }
            }
            
        if self.phic_no and not self.phic_no.isdigit():
            self.phic_no = ''
            return {
                'warning' : {
                'title': _('Warning'),
                'message':_('Invalid PHIC Format')
                }
           }
        
        if self.hdmf_no and not self.hdmf_no.isdigit():
            self.hdmf_no = ''
            return {
                'warning' : {
                'title': _('Warning'),
                'message':_('Invalid HDMF Format')
                }
           }
            
        if self.identification_id and not self.identification_id.isdigit():
            self.identification_id = ''
            return {
                'warning' : {
                'title': _('Warning'),
                'message':_('Invalid TIN Format')
               }
           }
    
    @api.multi
    def _default_country_id(self):
        country = self.env['res.country'].search([('code', '=', 'PH')], limit=1)
        return country

    @api.multi
    def print_barcode(self):
        for record in self.env['hr.employee'].search([]):
                record.barcode = record.employee_num

    @api.depends('employee_num')
    def get_employee_barcode(self):
        for record in self:
            record.barcode = record.employee_num

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widowed'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups='hr.group_hr_user', track_visibility = 'onchange')
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", related='employee_num', store=True, copy=False)
    firstname = fields.Char('First Name', size=16, required=True)
    lastname = fields.Char('Surname', size=16, required=True,track_visibility = 'onchange')
    middlename = fields.Char('Middle Name', size=16)
    age = fields.Float('Age', compute='_compute_age') 
    employee_num = fields.Char(required=True,string="Employee Number")
    street = fields.Char(related="address_home_id.street", string='Street')
    street2 = fields.Char(related="address_home_id.street2", string='Street')
    zip = fields.Char(related="address_home_id.zip", change_default=True)
    city2 = fields.Char(related="address_home_id.city", string='City')
    state_id = fields.Many2one(related="address_home_id.state_id", string='State', ondelete='restrict')
    country = fields.Many2one('res.country', string='Country', ondelete='restrict',default=_default_country_id)
    country_id = fields.Many2one(related="address_home_id.country_id", string='Country', ondelete='restrict')
   
    sss_no = fields.Char('SSS No', size=12, track_visibility = 'onchange')
    phic_no = fields.Char('PHIC No', size=12, track_visibility = 'onchange')
    hdmf_no = fields.Char('HDMF No', size=12, track_visibility = 'onchange')
    identification_id = fields.Char('TIN#', size=12, track_visibility = 'onchange')    
    
    work_location_id = fields.Many2one('hr.employee.work_location', 'Work Location')
    academic_experience = fields.One2many('hr.academic_experience','employee_id')
    
    attendance_code = fields.Char('Attendance Code')
    state = fields.Selection(emp_stages, string='Status', default='joined', track_visibility='always', copy=False,
                             help="Employee Stages.\nNewly Hired: Joined\nOn Boarding: Training\nProbationary period : Probation")

    auto_generate_barcode = fields.Boolean('Automatically Generate employee barcode')
    #branch_id = fields.Many2one('res.branch', 'Branch')
    hr_clearance_line = fields.One2many('hr.employee.clearance','employee_id')
    biometric_device_id = fields.Integer(string='Biometric Device ID')
    address = fields.Char(string='Address')
    id_company = fields.Many2one('res.company', string="Company")
    bank_account_no = fields.Integer('Bank Account Number')
    
class HRAcademicExperience(models.Model):
    _name = 'hr.academic_experience'
    _description = 'Academic Experiences'
    
    employee_id = fields.Many2one('hr.employee')
    acad_insti = fields.Char('Institution', size=16)

class HRHolidays(models.Model):
    _inherit = 'hr.holidays'

    company_id = fields.Many2one('res.company', string='Company')
    hr_payslip_id = fields.Many2one('hr.payslip', 'Payslip')


class ExtendedResCompany(models.Model):
    _inherit = 'res.company'

    sss_num = fields.Char(string="SSS No.")
    philhealth_num = fields.Char(string="PHIC No.")
    pagibig_num = fields.Char(string="HDMF No.")
    rdo_code = fields.Char('RDO Code')
    company_representative = fields.Char("Company Representative")

class HRJobCategory(models.Model):
    _name = 'hr.job.category'
    
    name = fields.Char('Category Name', required=True)
    job_line = fields.One2many('hr.job', 'job_categ_id', 'Jobs')
    
class HRJob(models.Model):
    _inherit = 'hr.job'
    
    levels = [
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV'),
    ]
    
    code = fields.Char('Code')
    job_categ_id = fields.Many2one('hr.job.category')
    level = fields.Selection(levels, 'Level')
    structure_id = fields.Many2one('hr.payroll.structure', 'Salary Structure')

class HREmployeeClearance(models.Model):
    _name = 'hr.employee.clearance'
    _description = 'Hr Employee Clearance'
    _rec_name = 'employee_id'
    
    @api.model
    def default_get(self,fields):
        res = super(HREmployeeClearance,self).default_get(fields)
        template = self.env['hr.employee.clearance.config'].search([])
     
        approvers = []
        for rec in template:
            for records in rec.hr_config_line:
                approver = {}
                approver['department_id'] = records.department_id.id
                approver['approver_id'] = records.approver_id.id 
                approver['cleared'] = False
                approvers.append(approver)
            res['survey_id'] = rec.survey_id and rec.survey_id.id
        res['clearance_approver_line'] = [(0,0, ap) for ap in approvers]
        
        return res
    
    @api.depends('clearance_approver_line','response_id','survey_id','response_id.state')
    def _compute_clearance(self):
        for record in self:
            if record.clearance_approver_line:
                record.cleared = all(record.clearance_approver_line.mapped('cleared')) \
                and record.response_id.state == 'done'
                
            else:
                record.cleared = False
                
    @api.depends('clearance_approver_line','response_id','survey_id','response_id.state')
    def _compute_date(self):
        for record in self:
            if record.clearance_approver_line:
                check_cleared = all(record.clearance_approver_line.mapped('cleared'))
                if check_cleared and record.response_id.state == 'done':
                    date_clear = record.clearance_approver_line.sorted(key=lambda r:r.date_cleared,reverse=True)
                    record.date_cleared = date_clear and date_clear[0].date_cleared
                    
    
    employee_id = fields.Many2one('hr.employee',string="Employee Name")
    date_cleared = fields.Date(string="Date Cleared",compute='_compute_date')
    cleared = fields.Boolean(string="Cleared",compute="_compute_clearance",store=True)
    clearance_approver_line = fields.One2many('hr.employee.clearance.approver','hr_employee_clearance_id')
    survey_id = fields.Many2one('survey.survey', string="Exit Interview Form")
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")

    @api.multi
    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.survey_id.id, 'partner_id': self.employee_id.user_id and self.employee_id.user_id.partner_id.id})
            self.response_id = response.id
            
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()

    @api.multi
    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_id:
            return self.survey_id.action_print_survey()
        else:
            response = self.response_id
            
            return self.survey_id.with_context(survey_token=response.token).action_print_survey()


class HREmployeeApprovers(models.Model):
    _name = 'hr.employee.clearance.approver'
    _description = 'HR Employee Clearance Approvers'
    _rec_name = 'department_id'
    
    department_id = fields.Many2one('hr.department', string="Department", required=True)
    approver_id = fields.Many2one('hr.employee', string="Approver", required=True)
    cleared = fields.Boolean(string="Cleared",default=False)
    date_cleared = fields.Date(string="Date Cleared")
    remarks = fields.Text(string="Remarks")
    hr_employee_clearance_id = fields.Many2one('hr.employee.clearance')

class HREmployeeClearanceConfig(models.Model):
    _name = 'hr.employee.clearance.config'
    _description = 'HR Employee Clearance Config'
    
    name = fields.Char('Name',required=True)
    active = fields.Boolean(string="Active", default=True)
    survey_id = fields.Many2one('survey.survey', string="Exit Interview Form")
    hr_config_line = fields.One2many('hr.employee.clearance.config.line','hr_clearance_config_id')
    
class HREmployeeClearanceConfigLine(models.Model):
    _name = 'hr.employee.clearance.config.line'
    _description = 'HR Employee Clearance Configuration Line'
    
    department_id = fields.Many2one('hr.department', string="Department", required=True)
    approver_id = fields.Many2one('hr.employee', string="Approver", required=True)
    hr_clearance_config_id = fields.Many2one('hr.employee.clearance.config')
   
