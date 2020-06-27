from odoo import api, fields, models
from odoo import tools, _
from datetime import date
from odoo.exceptions import ValidationError
import re

class  Employee(models.Model):
    _name = "emp.employee"
    _sql_constraints = [ ('code_unique', 'unique(code)', 'Code must be Unique!!!!') ]
    photo = fields.Binary(string="Employee Photo",help="Select image less than size of 100kb.", attachment=True)
    photo_medium = fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    name = fields.Char(string="Name",size=64,required="True")
    code = fields.Char(string="Code", size=7, unique="True", readonly=True)
    birth_date = fields.Date(string="Birth Date" ,required="True")
    gender = fields.Selection([('male','Male'),('female','Female'),],'Gender',required="True")
    marital_status = fields.Selection([('married','Married'),('unmarried','Unmarried'),],'Marital Status',required="False", default="2")
    childs = fields.Integer(string="Childs")
    address = fields.Text(string="Address",size=256, required="True")
    job_id = fields.Many2one("emp.job",string="Job Position")
    tag_ids = fields.Many2many( "emp.job.tags","emp_job_rel","emp_id","job_tag_id",string="Job Tags")
    joining_date = fields.Date(string="Joining Date",required="True")
    basic_salary = fields.Float(string="Basic Salary",required="True")
    is_manager = fields.Boolean(string="Is Manager?")
    manager_id = fields.Many2one("emp.employee",string="Manager",search="name_search")
    employee_ids = fields.One2many('emp.employee','manager_id', string='Employees')
    department_ids = fields.Many2one("emp.department", string="Department")
    color = fields.Integer('Color Index', default=0) 
    contract_ids = fields.One2many("emp.employee.contract","employee_id")

    @api.constrains('birth_date')
    def _check_something(self):
        today_date = date.today()
        date_list = self.birth_date.split("-")
        year = int(date_list[0])
        months = int(date_list[1])
        days = int(date_list[2])
        result = today_date.year - year - ((today_date.month, today_date.day) < (months, days))
        if result < 18:
            raise ValidationError("Your age is too short:")
    
    @api.constrains('email')
    def _validate_email(self):
        if re.match("^[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$",self.email) != None:
            return True
        else:
            raise ValidationError("Email-Id is not valid...")

    @api.model
    def create(self,vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('emp.employee')
        result = super(Employee,self).create(vals)
        return result

class Manager(models.Model):
    _name = "emp.manager"
    _inherits = {'emp.employee': 'employee_id'}
    employee_id = fields.Many2one("emp.employee")
    # _sql_constraints = [ ('code_unique', 'unique(code)', 'Code must be Unique!!!!') ]
    phone = fields.Char(string="Phone", size=10)
    email = fields.Char(string="Email", size=40)
    website = fields.Char(string="Website", size=50)
    total_employees = fields.Float(compute="_total_emp")
    manager_id = fields.Many2one("emp.employee",string="Manager" )
    total_employees = fields.Integer(compute="_total_emp")
    @api.depends('employee_ids')
    def _total_emp(self):
        count = 0
        for line in self.employee_ids:
            count = count + 1
        self._fields['total_employees'].__set__(self, count)

class JobPosition(models.Model):
    _name = "emp.job"
    _sql_constraints = [ ('code_unique', 'unique(code)', 'Code must be Unique!!!!') ]
    name = fields.Char(string="Name",size=64,required="True")
    code = fields.Char(string="Code",size=2,required="True",unique="True")
    employee_ids = fields.One2many("emp.employee","job_id",string="Employee ID")
    total_employees = fields.Float(compute="_total_emp")
    
    @api.depends('employee_ids')
    def _total_emp(self):
        count = 0
        for line in self.employee_ids:
            count = count + 1
        self._fields['total_employees'].__set__(self, count)

class JobTags(models.Model): 
    _name = "emp.job.tags"
    name = fields.Char(string="Name", size=64,required="True")
    employee_ids = fields.Many2many("emp.employee","emp_job_rel","job_tag_id","emp_id",string="Employess")
    total_employees = fields.Float(compute="_total_emp")
    color = fields.Integer('Color Index', default=1) 
    
    @api.depends('employee_ids')
    def _total_emp(self):
        count = 0
        for line in self.employee_ids:
            count = count + 1
        self._fields['total_employees'].__set__(self, count) 

class Department(models.Model):
    _name = "emp.department"
    _sql_constraints = [ ('code_unique', 'unique(code)', 'Code must be Unique!!!!') ]
    name = fields.Char(string="Name", size=64,required="True")
    code = fields.Char(string="Code",size=2,required="True",unique="True")
    employee_ids = fields.One2many("emp.employee","department_ids",string="Employees")
    total_employees = fields.Integer(compute='_total_emp' )
    
    @api.depends('employee_ids')
    def _total_emp(self):
        count = 0
        for line in self.employee_ids:
            count = count + 1
        self._fields['total_employees'].__set__(self, count)

        
class EmployeeContract(models.Model):
    _name = "emp.employee.contract"
    name = fields.Char(string="Name",size=64,required=True) 
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date",required=True)
    employee_id = fields.Many2one("emp.employee", string="Employee",required=True)
    basic_salary = fields.Float(string="Basic Salary",related="employee_id.basic_salary",readonly="True",required=True)
    job_id = fields.Many2one("emp.job",related="employee_id.job_id",string="Job Position",readonly="True",required=True)
    salary_structure_id = fields.Many2one("emp.employee.salary.structure",string="Salary Structure",required=True)
    salary_per_month = fields.One2many("emp.employee.month.salary","contract_name")

    state = fields.Selection([ 
        ('draft', 'Draft'), 
        ('running', 'Running'), 
        ('cancel', 'Closed'), ], 
        string='Emp Status', readonly=True, copy=False, store=True, default='draft')

    @api.multi
    def draft(self,vals):
        self.write({'state': 'draft'})

        
    @api.multi
    def running(self):
        self.write({'state': 'running'})
    
    @api.multi
    def close(self):
        self.write({'state': 'cancel'})

    @api.constrains('start_date','end_date')
    def date_validation(self):
            contracts = self.env['emp.employee.contract'].search([('employee_id', '=', self.employee_id.id)])
            count = 0
            for contract in contracts:
                startDate = contract.start_date
                endDate = contract.end_date
                if (startDate <= self.start_date and endDate >= self.end_date):
                    count +=1
                elif (startDate >= self.start_date and endDate >= self.end_date and self.end_date >= startDate ):
                    count += 1
                elif (startDate >= self.start_date and endDate <= self.end_date):
                    count += 1
                elif (startDate <= self.start_date and endDate <= self.end_date and self.start_date <= endDate):
                    count += 1
                else:
                    pass
            if count>1:
                raise ValidationError("Contract Already Running Between Start Date and End Date.\nSelect other Start Date and End Date.")
        
    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('name', _("%s (copy)") % (self.name or ''))
        default['start_date'] = False
        default['end_date'] = False
        default['employee_id'] = False
        default['salary_structure_id'] = False
        return super(EmployeeContract, self).copy(default)



class SalaryStructure(models.Model):
    _name = "emp.employee.salary.structure"

    name = fields.Char(string="Name",size=64)
    job_id = fields.Many2one("emp.job",string="Job Position")
    allowance_ids = fields.One2many("emp.salary.allowance.line","salary_structure_id",string="Allowances")

class SalaryAllowanceLine(models.Model):
    _name = "emp.salary.allowance.line"
    _rec_name = "allowance_id"

    salary_structure_id=fields.Many2one('emp.employee.salary.structure')
    allowance_id = fields.Many2one("emp.salary.allowance",string="Allowance")
    type1 = fields.Selection([('1','Allowance'),('2','Deduction'),],string="Type") 
    based_on = fields.Selection([('1','Fixed'),('2','Percentage'),],string="Based On")
    amount = fields.Float(string="Amount")

class EmployeeSalaryAllowance(models.Model):
    _name = "emp.salary.allowance"
    name = fields.Char(string="Name",size=64,required="True")

class EmployeePerMonthSalary(models.Model):
    _name = "emp.employee.month.salary"
    
    contract_name = fields.Many2one("emp.employee.contract",string="Contract Name" )
    month = fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),
        ('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')],required=True)
    basic_salary = fields.Float(required="True",readonly="True",related="contract_name.basic_salary")
    allowance = fields.Float()
    net_salary = fields.Float(readonly=True ,compute='_amount_all')
    deduction = fields.Float()
    gross_salary = fields.Float(compute='_amount_all')

    @api.depends('basic_salary','net_salary','gross_salary','allowance' ,'deduction')
    def _amount_all(self):
        for line in self:
            line.gross_salary = line.basic_salary + line.allowance
            line.net_salary = line.gross_salary - line.deduction

    @api.onchange('month')
    def _onchange_month(self):
        allowance = 0
        deduction = 0
        for line in self.contract_name.salary_structure_id.allowance_ids:
            if line.type1 == '1' and line.based_on =='1': 
                allowance += line.amount
            elif line.type1 == '1' and line.based_on =='2':
                allowance += line.amount * self.basic_salary/100
            elif line.type1 == '2' and line.based_on =='1': 
                deduction += line.amount
            elif line.type1 == '2' and line.based_on =='2':
                deduction += line.amount * self.basic_salary/100

        self.update({'allowance': allowance ,'deduction': deduction})

class EmployeeJobData(models.Model):
    _name = "emp.job.data"

    emp_id = fields.Many2one("emp.employee", string="Employee")
    job_id = fields.Many2one("emp.in.job.position",string="Job Position")


class EmployeeInJobPosition(models.Model):
    # first
    _name = "emp.in.job.position"
    _rec_name = "job_id"
    job_id = fields.Many2one("emp.job")
    employee_ids = fields.One2many("emp.job.data","job_id",string="Employee")

    def get_employee(self):
        employees = self.env['emp.employee'].search([('job_id', '=', self.job_id.id)])
        employee_line = []
        emp_id_list = []

        for line in self.employee_ids:
            emp_id_list.append(line.emp_id.id)

        for line in employees:
            if line.id not in emp_id_list:
                employee_line.append([0,0,{'emp_id': line.id}])
        
        self.write({'employee_ids': employee_line})
        return True

class EmployeeAllowanceData(models.Model):
    #for second
    _name = "employee.allowance.data"
    _rec_name = "allowances"

    allowances = fields.Many2one("emp.salary.allowance.line", "Allowance Line" )
    salary_structure_id = fields.Many2one("emp.allowance.lines")

class EmployeeAllownceLines(models.Model):
    # second
    _name = "emp.allownce.lines"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("emp.employee",string="Employee")
    allowance_ids = fields.One2many("employee.allowance.data", "salary_structure_id" )

    def get_allowance_lines(self):
        contracts = self.env['emp.employee.contract'].search([('employee_id','=',self.employee_id.id)])
        allowance_line = []
        allowance_id_list = []
        
        for line in self.allowance_ids:
            allowance_id_list.append(line.allowances.id)

        for line in contracts[0].salary_structure_id.allowance_ids:
            if line.id not in allowance_id_list:
                allowance_line.append([0,0,{'allowances': line.id}])
        self.write({'allowance_ids': allowance_line})
        return True

class ContractData(models.Model):
    _name = "contract.data"

    contract_id = fields.Many2one("emp.employee.contract")
    contract = fields.Many2one("contract.status")

class ContractStatus(models.Model):
    # third
    _name = "contract.status"

    start_date = fields.Date(string="Start Date",required="True")
    end_date = fields.Date(string="End Date",required="True")
    contracts = fields.One2many("contract.data","contract")

    @api.multi
    def fetch_contract(self):
        contract_ids = self.env['emp.employee.contract'].search([])
        contract_record = contract_ids.filtered(lambda val: val.start_date >=self.start_date and val.end_date <= self.end_date and val.state == 'running' )
        contract_line = []

        for line in contract_record:
                contract_line.append([0,0,{'contract_id': line.id}])
        self.write({'contracts': contract_line})
        # self.contracts = [(6,0,contract_ids.filtered(lambda val: val.start_date >=self.start_date and val.end_date <= self.end_date and val.state == 'running' ).ids)]

class EmployeeAndContract(models.Model):
    #fourth
    _name = "employee.and.contract"

    name = fields.Char(string="Name",size=64,required="True")
    birth_date = fields.Date(string="Birth Date" ,required="True")
    gender = fields.Selection([('male','Male'),('female','Female'),],'Gender',required="True")
    address = fields.Text(string="Address",size=256, required="True")
    job_id = fields.Many2one("emp.job",string="Job Position",required="True")
    joining_date = fields.Date(string="Joining Date",required="True")
    basic_salary = fields.Float(string="Basic Salary",required="True")
    manager_id = fields.Many2one("emp.employee",string="Manager",required=True)
    contract_name = fields.Char(string="Name",size=64,required=True) 
    start_date = fields.Date(string="Start Date",required=True)
    end_date = fields.Date(string="End Date",required=True)
    salary_structure_id = fields.Many2one("emp.employee.salary.structure",string="Salary Structure",required=True)
    employee_id = fields.Many2one("emp.employee")
    contract_id = fields.Many2one("emp.employee.contract")
   
    @api.multi
    def create_employee_and_contract(self):
        self.employee_id = self.env['emp.employee'].create({'name': self.name,
            'birth_date': self.birth_date,
            'gender':self.gender, 'address':self.address, 
            'job_id':self.job_id.id,'joining_date': self.joining_date,
            'basic_salary': self.basic_salary,'manager_id':self.manager_id.id})

        self.contract_id = self.env['emp.employee.contract'].create({'name':self.contract_name,
            'start_date':self.start_date,'end_date':self.end_date,
            'job_id': self.job_id.id,'basic_salary':self.basic_salary,
            'salary_structure_id': self.salary_structure_id.id, 'employee_id':self.employee_id.id})

    @api.multi
    def update_employee_and_contract(self):
        self.employee_id.write({'name': self.name,'birth_date': self.birth_date,
                'gender':self.gender, 'address':self.address, 'job_id':self.job_id.id,
                'joining_date': self.joining_date,'basic_salary': self.basic_salary,
                'manager_id':self.manager_id.id})
        
        self.contract_id.write({'name':self.contract_name,'start_date':self.start_date,
            'end_date':self.end_date,'job_id': self.job_id.id,'basic_salary':self.basic_salary,
            'salary_structure_id': self.salary_structure_id.id })

    @api.multi
    def delete_employee_and_contract(self):
        self.employee_id.unlink()
        self.contract_id.unlink()


class TotalSalary(models.Model):
    _name = "total.salary"
    _rec_name = "job_id"

    job_id = fields.Many2one("emp.job")
    department_id = fields.Many2one("emp.department")
    tag_ids = fields.Many2many("emp.job.tags")
    total_salary = fields.Float(string="Total Salary", compute="all_calculation")
    allownce = fields.Float(string="Allowance", compute="all_calculation" )
    deduction = fields.Float(string="Deduction", compute="all_calculation")
    net_salary = fields.Float(string="Net Salary", compute="all_calculation")
    contracts = fields.Many2many("emp.employee.contract")

    @api.multi
    def get_contracts(self):
        contract_ids = self.env["emp.employee.contract"].search([])
        self.contracts = [(6,0,contract_ids.filtered(lambda val: val.job_id == self.job_id and 
            val.employee_id.department_ids == self.department_id and 
            val.employee_id.tag_ids == self.tag_ids ).ids)]
        
    def all_calculation(self):
        total_salary = allowance = deduction = net_salary = 0.0
        
        for record in self.contracts:
            for line in record.salary_per_month:
                total_salary += line.basic_salary
                allowance += line.allowance
                deduction += line.deduction

        self.update({'total_salary': total_salary, 
                     'allownce': allowance,
                     'deduction': deduction, 
                     'net_salary': total_salary + allowance - deduction })