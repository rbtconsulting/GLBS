# TEST
import psycopg2

try:
	cnx = psycopg2.connect("host=localhost dbname='payroll2' user='odoo007' password='odoo007' port=5432")
	crs = cnx.cursor()

except psycopg2.Error as e:
	print e

crs.execute("""
	SELECT pl.code, sum(pl.total), w.code, sum(w.number_of_hours)
                FROM hr_payslip_line AS pl
                LEFT JOIN hr_payslip AS p ON pl.slip_id=p.id
                LEFT JOIN hr_employee AS he ON he.id=p.employee_id
                LEFT JOIN hr_payslip_worked_days as w ON w.payslip_id=p.id
                WHERE w.code='DTR'
                GROUP BY pl.code, w.code LIMIT 10
	""")
res = crs.fetchall()

print res