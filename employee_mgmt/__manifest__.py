# -*- coding: utf-8 -*-

{
    'name': 'Employee Management System',
    'version': '1.0',
    'category': 'Management System',
    'sequence': 75,
    'depends': ['base'],
    'summary': 'Employee Management System',
    'description': """
Demo Module
===========

This application enables you to manage important aspects of your company's staff and other details such as their skills, contacts, working time...


You can manage:
---------------
* Employees and hierarchies : You can define your employee with User and display hierarchies
* HR Departments
* HR Jobs
    """,
    'data': [
        'views/employee_mgmt_view.xml',
        'wizard/employee_mgmt_department_employee_view.xml',
	    'wizard/employee_mgmt_dep_manager_employee_view.xml',
        'wizard/employee_mgmt_jobposition_wise_employee_view.xml',
        'wizard/employee_mgmt_contract_wise_employee_view.xml',
        'wizard/employee_mgmt_convert_to_manager_view.xml',
        'wizard/employee_mgmt_close_contract_view.xml',
        'data/employee_mgmt_job_position.xml',
        'data/employee_mgmt_job_tags.xml',
        # 'demo/Employee_data.xml',
    ],
    # 'demo': [
    #     'demo/Employee_data.xml',
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}

