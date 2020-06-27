from odoo import api, fields, models

class DepartmentWiseEmployee(models.TransientModel):
    _name = "department.employee"
    
    department_ids = fields.Many2many("emp.department",string="Department:")

    def open_employee_tree(self):
    	action = self.env.ref('employee_mgmt.open_demo_form_act')
    	result = action.read()[0]
    	result['domain'] = [('department_ids', 'in', self.department_ids.ids)]
    	result['context'] = {'group_by': ['department_ids']}
    	return result