from odoo import api, fields, models

class ContractWiseEmployee(models.TransientModel):
    _name = "contract.job.employee"
    
    start_date = fields.Date(string="Start Date:")
    end_date = fields.Date(string="End Date:")
    job_id = fields.Many2one("emp.job",string="Job Position:")

    def open_employee_tree(self):
        action = self.env.ref('employee_mgmt.open_demo_form_act')
    	contracts = self.env['emp.employee.contract'].search([])
        contract_record = contracts.filtered(lambda val: val.start_date >=self.start_date and val.end_date <= self.end_date and val.job_id.id == self.job_id.id)
        result = action.read()[0]
        employees = []
        for record in contract_record:
            employees.append(record.employee_id.code)
            result['domain'] = [('code', 'in', employees)]
        	return result