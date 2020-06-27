from odoo import api, fields, models

class ManagerDeparmentWiseEmployee(models.TransientModel):
    _name = "manager.department.employee"
    
    department_ids = fields.Many2many("emp.department",string="Departments:")
    manager_id = fields.Many2one("emp.manager",string="Manager:")

    def open_employee_tree(self):
    	action = self.env.ref('employee_mgmt.open_demo_form_act')
    	result = action.read()[0]
    	result['domain'] = [('department_ids', 'in', self.department_ids.ids),
    						('manager_id', '=', self.manager_id.id)]
    	
    	return result