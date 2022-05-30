# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api

class PayrollCustomReportView(models.Model):
	_name = 'hr.payroll.custom.report.view'
	_auto = False

	name = fields.Many2one('hr.employee', string='Employee')
	date_from = fields.Date(string='From')
	date_to = fields.Date(string='To')
	state = fields.Selection([('draft', 'Draft'), ('verify', 'Waiting'), ('done', 'Done'), ('cancel', 'Rejected')],
                             string='Status')
	job_id = fields.Many2one('hr.job', string='Job Title')
	company_id = fields.Many2one('res.company', string='Company')
	department_id = fields.Many2one('hr.department', string='Department')
	net = fields.Float(string='Net Salary')
	basic = fields.Float(string='Basic Salary')
	gross = fields.Float(string='Gross Salary')
	tax = fields.Float(string='Tax')

	@api.model_cr
	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		qry = """
			SELECT 
				ps.id as id,
				ps.state as state,
				emp.id as name,
				jb.id as job_id,
				dp.id as department_id,
				cmp.id as company_id,
				ps.date_from,
				ps.date_to,
				COALESCE((SELECT psl.total FROM hr_payslip_line as psl WHERE code='NET' AND ps.id=psl.slip_id), 0.00) as net,
				COALESCE((SELECT psl.total FROM hr_payslip_line as psl WHERE code='BASIC' AND ps.id=psl.slip_id), 0.00) as basic,
				COALESCE((SELECT psl.total FROM hr_payslip_line as psl WHERE code='PT' AND ps.id=psl.slip_id), 0.00) as tax,
				COALESCE((SELECT psl.total FROM hr_payslip_line as psl WHERE code='GROSS' AND ps.id=psl.slip_id), 0.00) as gross
			FROM hr_payslip as ps
			JOIN hr_employee as emp ON (ps.employee_id=emp.id)
			JOIN hr_department dp ON (emp.department_id=dp.id)
			JOIN hr_job jb ON (emp.job_id=jb.id)
			JOIN res_company as cmp ON (cmp.id=ps.company_id)
		"""
		self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( %s)
			""" % (self._table, qry))