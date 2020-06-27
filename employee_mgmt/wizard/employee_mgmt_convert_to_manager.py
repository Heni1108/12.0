from odoo import api, fields, models

class ChangePosition(models.TransientModel):
    _name = "convert.to.manager"
    is_manager = fields.Boolean(nolabel=True)
    
    def change_position(self):
    	employee = self.env['emp.employee'].search([('id', '=', self._context['active_id'])])
    	if self.is_manager:
	    	if employee.is_manager:
	    		employee.write({'is_manager': False})
	    	else:
	    		employee.write({'is_manager': True})
