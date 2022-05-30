Customizations of Human Resource modules
===========================================

Key Features
---------------

*  Three level of Access Rights

*  Payroll Registry, Statutory and BIR Reports

*  Payroll Statutory Tables

*  Recruitment and Employee 201 File

*  Leaves Allocation and Conversion Automation

*  Manage Employee Other Income, Salary Movement

*  Timekeeping and Attedance Monitoring 

*  Manage Multiple Work Schedule

*  Request for Change of Attendance

Method that can be called on salary rule
=========================================

* get_other_income - Returns employee other income based on code.
	* @args {string} code - The other income code
	* @args {object} payslip - The payslip object
	* @args {object} employee - The employee object
	* @args {object} contract - The contract object	

Example
--------


```python
	
	result = contract.get_other_income('RS', payslip, employee, contract)
``` 
