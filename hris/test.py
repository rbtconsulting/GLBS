# -*- encoding: utf-8 -*-

import psycopg2

cnx = psycopg2.connect("host=localhost dbname=odoo10 user=postgres password=postgres")
crs = cnx.cursor()

def test():
	l = [{'1':'1'},{},{'2':'2'}]

	d = {}
	for i in l:
		print i
		if i:
			d.update(i)

	print d

	s =[
		[[{u'Basic': 5000.0}, {u'Allowance': 3620.0}, {u'Gross': 8620.0}, {u'Deduction': -825.0}, {u'Net': 7795.0}, {}, {}, {}, {}, {}, {}, {}]], 
		[[{u'Basic': 15000.0}, {}, {u'Gross': 15706.9}, {u'Deduction': 862.07}, {u'Net': 14838.4}, {}, {u'OT (Normal Day)': 431.03}, {u'Night Shift Differential': 34.48}, {u'Rest Day Work': 896.55}, {u'Special Non-working Day': 206.9}, {u'Contribution': 868.5}, {u'Withholding Tax': 1483.84}]]
	]

	def rename_key(key):
		key = key.lower()
		_str = ''
		for k in key:
			if k not in 'abcdefghijklmnopqrstuvwxyz':
				_str += '_'
			else:
				_str += k
		return _str

	print rename_key('a dafdf-a a')

	x = [{'1':'2'},]
	y = [{'12':'22'},]

	z = x + y

	for z1 in z:
		print z1

def query(emp_id, mnth, year):

	#qry = "SELECT id, name_related FROM hr_employee"
	#crs.execute(qry)

	#res = crs.fetchall()

	#print res
	# Juan Dela Cruz 24
	# Ashley Presley 12

	# 1 for January is an issue it should be 01

	qry = """
			SELECT pl.code, pl.total
			FROM hr_payslip_line AS pl
			LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
			LEFT JOIN hr_employee AS emp ON emp.id = p.employee_id
			LEFT JOIN resource_resource AS r ON r.id = emp.resource_id
			WHERE p.state = 'done' AND p.employee_id = {}
			AND to_char(date_to,'mm-yyyy') = '{}'
			GROUP BY pl.code, pl.total
		""".format(emp_id, str(mnth)+'-'+str(year))

	print qry

	crs.execute(qry)
	res = crs.fetchall()

	print res
	

#query(12, '01', '2018')

#print '01-2017'.split('-')
def _enumerate():
	for x, y in enumerate([1, 3, 4]):
		print x, y

def payroll_registry(start_date, end_date):
	qry = """
		SELECT pl.code, sum(pl.total)
		FROM hr_payslip_line AS pl
		LEFT JOIN hr_payslip AS p ON pl.slip_id = p.id
		LEFT JOIN hr_employee AS he ON he.id = p.employee_id
		WHERE to_char(date_from, 'mm-dd-yyyy') = '{}' AND to_char(date_to, 'mm-dd-yyyy') = '{}'
		AND p.state = 'done'
		GROUP BY pl.code
	""".format(start_date, end_date)

	print qry

	crs.execute(qry)
	res = crs.fetchall()
	print dict(res)

payroll_registry('01-01-2018','01-31-2018')