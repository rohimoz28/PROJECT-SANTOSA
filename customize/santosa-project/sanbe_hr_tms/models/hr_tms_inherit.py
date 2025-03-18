from odoo import fields, models, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

class HrEmployeeMutation(models.Model):
    _inherit = 'hr.employee.mutations'
    
class Contract(models.Model):
    _inherit = 'hr.contract'
    
class HRWarningLeter(models.Model):
    _inherit = 'hr.warning.letter'

class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'
    
# class HrDocument(models.Model):
#     _inherit = 'hr.document'
    
# class HrResignation(models.Model):
#     _inherit = 'hr.resignation'

# class SalaryAdvance(models.Model):
#     _inherit = 'salary.advance'
    
# class HrLoan(models.Model):
#     _inherit = 'hr.loan'
    
# class HrEmployeeSkillReport(models.BaseModel):
#     _inherit = 'hr.employee.skill.report'
    
class HrDepartment(models.Model):
    _inherit = 'hr.department'

# class ContractType(models.Model):
#     _inherit = 'hr.contract.type'
    
# class WorkLocation(models.Model):
#     _inherit = 'hr.work.location'
    
# class SkillType(models.Model):
#     _inherit = 'hr.skill.type'
    
# class HrJob(models.Model):
#     _inherit = 'hr.job'
    
# class DocumentType(models.Model):
#     _inherit = 'document.type'
    
# class HRServiceType(models.Model):
#     _inherit = 'hr.services.types'
    
# class HRJobStatus(models.Model):
#     _inherit = 'hr.job.status'
    
# class HREmployementStatus(models.Model):
#     _inherit = 'hr.employement.status'
    
# class HRPasalPelanngaran(models.Model):
#     _inherit = 'hr.pasal.pelanggaran'
    
# class HRWarningLeterType(models.Model):
#     _inherit = 'hr.warning.lettertype'
    
# class CertificationType(models.Model):
#     _inherit = 'certification.type'
    
# class EmployeeLeveling(models.Model):
#     _inherit = 'employee.level'