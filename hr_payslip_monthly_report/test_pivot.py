import psycopg2

try:
	cnx = psycopg2.connect("host=localhost user=openerp password=postgres dbname=odoo10")
	crs = cnx.cursor()
except postgres.Error as e:
	print e

qry = """
        SELECT pl.code, pl.total
            FROM hr_payslip_line AS pl
        LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
        LEFT JOIN hr_employee AS emp ON emp.id = p.employee_id
        LEFT JOIN resource_resource AS r ON r.id = emp.resource_id
        WHERE p.state = 'done' AND p.employee_id = {}
        AND to_char(date_to,'mm-yyyy') = '{}'
        GROUP BY pl.code, pl.total
      """

qry2 = """
	SELECT
				min(p.id) as id,
				emp.name_related,
				p.state as state,
				emp.id as name,
				jb.id as job_id,
				dp.id as department_id,
				cmp.id as company_id,
				p.date_from,
				p.date_to,
				sum(net.net_total) as net,
				sum(basic.basic_total) as basic,
				sum(gross.gross_total) as gross
				
			FROM hr_payslip p
			JOIN hr_employee as emp ON (p.employee_id=emp.id)
			JOIN hr_department dp ON (emp.department_id=dp.id)
			JOIN hr_job jb ON (emp.job_id=jb.id)
			JOIN res_company as cmp ON (cmp.id=p.company_id)
			JOIN (
				SELECT pl.slip_id, sum(pl.total) as net_total
				FROM hr_payslip_line as pl WHERE pl.code='NET'
				GROUP by pl.slip_id
			) as net ON net.slip_id = p.id
			JOIN (
				SELECT pl.slip_id, sum(pl.total) as basic_total
				FROM hr_payslip_line as pl WHERE pl.code='BASIC'
				GROUP by pl.slip_id
			) as basic ON basic.slip_id = p.id
			JOIN (
				SELECT pl.slip_id, sum(pl.total) as gross_total
				FROM hr_payslip_line as pl WHERE pl.code='GROSS'
				GROUP by pl.slip_id
			) as gross ON gross.slip_id = p.id
			
			
			GROUP BY emp.id, dp.id, jb.id, cmp.id, p.date_from, p.date_to, 
					 p.state, net.net_total, basic.basic_total, gross.gross_total
			"""

qry3 = """
	SELECT 
		ps.id as id,
		ps.state as state,
		emp.id as name,
		jb.id as job_id,
		dp.id as department_id,
		cmp.id as company_id,
		ps.date_from,
		ps.date_to,
		(SELECT psl.total FROM hr_payslip_line as psl WHERE code='NET' AND ps.id=psl.slip_id) as net,
		(SELECT psl.total FROM hr_payslip_line as psl WHERE code='BASIC' AND ps.id=psl.slip_id) as basic,
		(SELECT psl.total FROM hr_payslip_line as psl WHERE code='PT' AND ps.id=psl.slip_id) as tax,
		(SELECT psl.total FROM hr_payslip_line as psl WHERE code='GROSS' AND ps.id=psl.slip_id) as gross
	FROM hr_payslip as ps
	JOIN hr_employee as emp ON (ps.employee_id=emp.id)
	JOIN hr_department dp ON (emp.department_id=dp.id)
	JOIN hr_job jb ON (emp.job_id=jb.id)
	JOIN res_company as cmp ON (cmp.id=ps.company_id)
"""

qry4 = """
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
crs.execute(qry4)
res = crs.fetchall()

print res