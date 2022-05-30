# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from datetime import datetime, date
from openerp.exceptions import UserError, ValidationError


mapping = ['sys_process','follow_instr','flexible','plan','job_knowledge','skill','learn_skill','accuracy','reliability','cust_sati','work_comple','pressure','handling','relationship','prob_solv','dec_mak','time_mng','express','share_know',
              'seeks','open_ideas','enthu','trust','ettiquttes','punctuality','descipline','attendance','team_work','team_build','strategy', 'participation']
mapping_avg = ['sys_process','follow_instr','flexible','plan','job_knowledge','skill','learn_skill','accuracy','reliability','cust_sati','work_comple','pressure','handling']


class hr_job(models.Model):
    _inherit = 'hr.job'

    kra_id = fields.Many2one('hr.kra', 'KRA')


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _kra_count(self):
        for rec in self:
            print "Yooooo"
            kras = self.env['employee.kra'].search([('employee_id', '=', rec.id)])
            rec.kra_count = len(kras)

    @api.multi
    def _value_rating_count(self):
        for rec in self:
            print "hooooo"
            value_ratings = self.env['value.rating'].search([('employee_id', '=', rec.id)])
            rec.value_rating_count = len(value_ratings)

    kra_id = fields.Many2one('hr.kra', related='job_id.kra_id', string="KRA", readonly=True)
    employee_code = fields.Integer('Employee Code')
    kra_count = fields.Integer(compute='_kra_count', string="KRA")
    value_rating_count = fields.Integer(compute='_value_rating_count', string="Value Ratings")

    @api.multi
    def action_kra_tree_view(self):
        return {
            'name': 'Employee KRA',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'employee.kra',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', 'in', self.ids)],
        }

    @api.multi
    def action_value_rating_tree_view(self):
        return {
            'name': 'Employee Value Rating',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'value.rating',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', 'in', self.ids)],
        }

class employee_kra(models.Model):
    _name = 'employee.kra'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    name = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'october'), (11, 'November'), (12, 'December') ], "KRA Month", required=True)
    quarterly = fields.Selection([(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')], "KRA Quarter")
    year = fields.Many2one('employee.year', 'Year', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    kra_id = fields.Many2one('hr.kra', related='employee_id.kra_id', string="KRA", readonly=True)
    kra_question_ids = fields.One2many('employee.kra.question', 'employee_kra_id', 'KRA Question')
    date = fields.Date("Date", default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submited To Supervisor'), ('cancel', 'Cancelled'), ('done', 'Done'), ], "State", track_visibility='onchange', default='draft')

    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.onchange('employee_id')
    def onchange_employee(self):
        data = []
        for que in self.employee_id.job_id.kra_id.kra_question_ids:
            data.append((0,0,{
                'employee_id': self.employee_id.id,
                'name': que.name,
                'description': que.description,
                'weightage': que.weightage,
                'kra_question_id': que.id, 
                #'employee_kra_id': self.id,
                'sequence': que.sequence,
                'hint': que.hint}))
        self.kra_question_ids = data

class employee_kra_question(models.Model):
    _name = 'employee.kra.question'
    _order = 'sequence'

    @api.multi
    @api.depends('manager_rating')
    def _compute_total(self):
        for que in self:
            que.final_score = (que.weightage * que.manager_rating) / 10

    @api.multi
    def _check_max_limit(self):
        for que in self:
             if (que.employee_rating < 0.0 or que.employee_rating > 10.0):
                 return False
             if (que.manager_rating < 0.0 or que.manager_rating > 10.0):
                 return False
        return True

    name = fields.Char('Question')
    sequence = fields.Integer('Sr.No')
    description = fields.Text('Description')
    hint = fields.Char('Hint')
    employee_kra_id = fields.Many2one('employee.kra', 'KRA', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    kra_question_id = fields.Many2one('kra.question', 'KRA Question')
    employee_remark = fields.Char('Employee Remark')
    manager_remark = fields.Char('Manager Remark')
    employee_rating = fields.Float('Employee Rating')
    manager_rating = fields.Float('Manager Rating')
    weightage = fields.Integer('Weightage')
    final_score = fields.Float(compute='_compute_total', string='Final Score', store=True,readonly='1')

    _constraints = [
        (_check_max_limit, 'Rating in between 0-10 only', ['employee_rating', 'manager_rating'])
    ]

class hr_kra(models.Model):
    _name = 'hr.kra'
    _inherit = ['mail.thread']

    @api.multi
    def _check_allocation(self):
        total = 0.0
        for percentage in self:
            for amount in percentage.kra_question_ids:
                total += amount.weightage
            if total == 100 or total == 0:
                return True
        return False

    name = fields.Char('Name', required=True)
    kra_question_ids = fields.One2many('kra.question', 'kra_id', 'KRA Question')

    _constraints = [
        (_check_allocation, 'Warning!| The total Weightage distribution should be 100%.', ['kra_question_ids']), 
    ]

class kra_question(models.Model):
    _name = 'kra.question'
    _order = 'sequence'

    sequence = fields.Integer('Sr.No')
    kra_id = fields.Many2one('hr.kra', 'KRA', ondelete='cascade')
    name = fields.Char('Question')
    description = fields.Text('Description')
    hint = fields.Char('Hint')
    weightage = fields.Integer('Weightage')
    

class value_rating(models.Model):
    _name = 'value.rating'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    @api.multi
    def _check_max_limit(self):
        for values in self:
            for val in mapping:
                if (values[val] < 0.0 or values[val] > 5.0):
                 return False
        return True

    @api.multi
    def calculate_avg(self):
        res = 0.0
        for rec in self:
            total = 0.0
            for val in mapping_avg:
                total += rec[val]
            self.score_leader =  round((total /len(mapping_avg)), 2)

    @api.multi
    def total_average(self):
        for rec in self:
            total = 0.0
            for val in mapping:
                total += rec[val]
            self.total_avg =  round((total /len(mapping)), 2)

    employee_id = fields.Many2one('hr.employee', 'Employee Name', required=True)
    employee_code = fields.Integer(related='employee_id.employee_code', string="Employee Code" ,readonly=True)
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'),
                              (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], 'Month', required=True)
    year = fields.Many2one('employee.year', 'Year', required=True)
    designation = fields.Many2one('hr.job', related='employee_id.job_id', string='Designation', readonly=True)
    appraiser_id = fields.Many2one('hr.employee', related='employee_id.parent_id', string="Appraiser", store=True, readonly=True)
    sys_process = fields.Float('System and Processes')
    follow_instr = fields.Float('Follow Instructions')
    flexible = fields.Float('Adaptable and Flexible')
    plan = fields.Float('Ability To Plan')
    job_knowledge = fields.Float('Job Knowledge')
    skill = fields.Float('Skill To Handle Work')
    learn_skill = fields.Float('Learn New Skill')
    accuracy = fields.Float('Accuracy')
    reliability = fields.Float('Reliability')
    cust_sati = fields.Float('Client Satisfaction')
    work_comple = fields.Float('Work Completion On Time')
    pressure = fields.Float('Ability to work under pressure')
    handling = fields.Float('Handling new portfolio')
    score_leader = fields.Float(compute="calculate_avg" , string='Leadership Score', readonly='1',
        help="This shows avg value for fields of foru sections: Approach To Work, Technical Skills, Quality Of work, Handling Targets")
    relationship = fields.Float('Relationship with co-workers')
    prob_solv = fields.Float('Problem solving')
    dec_mak = fields.Float('Decision making')
    time_mng = fields.Float('Time management')
    express = fields.Float('Oral and written expression')
    share_know = fields.Float('Sharing of knowledge')
    seeks = fields.Float('Seeks T & D')
    open_ideas = fields.Float('Open to ideas')
    enthu = fields.Float('Enthusiastic')
    trust = fields.Float('Trustworthy')
    ettiquttes = fields.Float('Work Place ettiquttes')
    punctuality = fields.Float('Punctuality')
    descipline = fields.Float('Descipline')
    attendance = fields.Float('Attendance')
    team_work = fields.Float('Team work')
    team_build = fields.Float('Team Building')
    strategy = fields.Float('New Strategy and direction')
    participation = fields.Float('Participation in HR activities')
    total_avg = fields.Float(compute='total_average' , string='Total average', readonly='1')
    state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancelled'), ('done', 'Done'), ], "State" ,track_visibility='onchange',default='draft')

    _constraints = [
        (_check_max_limit, 'Value Rating in between 0-5 only', ['sys_process','follow_instr','flexible','plan','job_knowledge','skill','learn_skill','accuracy','reliability','cust_sati','work_comple','pressure','handling','relationship','prob_solv','dec_mak','time_mng','express','share_know',
                                                                'seeks','open_ideas','enthu','trust','ettiquttes','punctuality','descipline','attendance','team_work','team_build','strategy', 'participation']),
    ]

    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_done(self):
        self.state = 'done'


class employee_year(models.Model):
    _name = 'employee.year'

    name = fields.Char('Year', size=4)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
