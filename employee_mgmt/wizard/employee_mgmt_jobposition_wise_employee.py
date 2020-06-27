from odoo import api, fields, models

class JobPositionWiseEmployee(models.TransientModel):
    _name = "job.position.employee"
    
    job_id = fields.Many2one("emp.job",string="Job Tags:")
    tag_ids = fields.Many2many("emp.job.tags",string="Job Position:")

    def open_employee_tree(self):
    	action = self.env.ref('employee_mgmt.open_demo_form_act')
    	result = action.read()[0]
    	result['domain'] = [('tag_ids', 'in', self.tag_ids.ids),
    						('job_id', '=', self.job_id.id)]
    	
    	return result