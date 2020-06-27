from odoo import api, fields, models

class CloseContract(models.TransientModel):
    _name = "close.contract"
    
    contract_ids = fields.Many2many("emp.employee.contract", domain=([('state', '=', 'running')]),string="Contracts:")

    def close_contracts(self):
    	for contract in self.contract_ids:
            contract.update({'state': 'cancel'})
        return True