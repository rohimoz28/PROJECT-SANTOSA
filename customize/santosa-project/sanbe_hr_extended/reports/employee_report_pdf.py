from odoo import models, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


gender_map = {
    'male': 'Laki - laki',
    'female': 'Perempuan',
    'other': 'Lainnya'
}

class EmployeeReportHTML(models.AbstractModel):
    _name = 'report.sanbe_hr_extended.employee_report_html'
    _description = 'Employee Report HTML'


    @api.model
    def _get_report_values(self, docids, data=None):

        if not docids:
            active_ids = self.env.context.get('active_ids', [])
            active_model = self.env.context.get('active_model', 'hr.employment.log')
            
            if not active_ids:
                raise UserError(_("Tidak Ada data untuk record"))
            
            lines = self.env[active_model].browse(active_ids)
        else:
            lines = self.env['hr.employment.log'].browse(docids)

        # Prepare report data
        start_date_filter = data.get('start_date_filter')
        end_date_filter = data.get('end_date_filter')
        employee_group1s = data.get('employee_group1s')
        employee_levels = data.get('employee_levels')
        branch_id = data.get('branch_id')

        MUTATION_TYPES = ['CONF', 'PROM', 'DEMO', 'ROTA', 'MUTA', 'ACTV', 'CORR']
        EXIT_TYPES = ['RESG', 'TERM', 'EOCT', 'RETR', 'TFTG', 'PSAW', 'LOIL']
        new_types = 'NEWS'

        mutation_lines = []
        exit_lines = []
        new_lines = []

        index_mutation = 1
        index_exit = 1
        index_new  = 1

        for obj in lines:
            try:
                stype = (obj.service_type or '').upper()
                if stype in MUTATION_TYPES:
                    mutation_data = {
                        'no': index_mutation,
                        'nik': obj.employee_id.nik,
                        'name': obj.employee_id.name,
                        'job_id': obj.employee_id.job_id.name if obj.employee_id.job_id else '',
                        'service_type': stype,
                        'birthday': obj.employee_id.birthday or '',
                    }
                    mutation_lines.append(mutation_data)
                    index_mutation += 1 
                elif stype in EXIT_TYPES:
                    exit_data = {
                        'no': index_exit,
                        'nik': obj.employee_id.nik,
                        'name': obj.employee_id.name,
                        'job_id': obj.employee_id.job_id.name if obj.employee_id.job_id else '',
                        'service_type': stype,
                        'birthday': obj.employee_id.birthday or '',
                        'gender' : gender_map.get(obj.employee_id.gender or ''),
                        'no_ktp' : obj.employee_id.no_ktp or '',
                        'start_date' : obj.start_date or '',
                    }
                    exit_lines.append(exit_data)
                    index_exit += 1
                elif stype == new_types:
                    new_data = {
                        'no': index_new,
                        'nik': obj.employee_id.nik,
                        'name': obj.employee_id.name,
                        'job_id': obj.employee_id.job_id.name if obj.employee_id.job_id else '',
                        'birthday': obj.employee_id.birthday or '',
                        'gender' : gender_map.get(obj.employee_id.gender or ''),
                        'no_ktp' : obj.employee_id.no_ktp or '',
                        'start_date' : obj.start_date or '',
                        'contract_id' : obj.employee_id.contract_id.name or '',
                        'bank_account_id' : obj.employee_id.bank_account_id.acc_number or '',
                        'no_npwp' : obj.employee_id.no_npwp or '',
                        'parent_id' : obj.employee_id.parent_id.name or '',
                        'title' : obj.employee_id.title or '',
                        'service_type': stype,
                    }
                    new_lines.append(new_data)
                    index_new += 1 
            except Exception as e:
                _logger.info(f"Error processing record: {e}")

        # _logger.info(f"Processing row {index_mutation}: {mutation_lines}")
        # _logger.info(f"Processing row {index_exit}: {exit_lines}")
        # _logger.info(f"Processing row {index_new}: {new_lines}")

        return {
            'doc_model': 'hr.employment.log',
            'docs': lines,
            'mutation_lines': mutation_lines,
            'exit_lines': exit_lines,
            'new_lines' : new_lines,
            'start_date_filter': start_date_filter,
            'end_date_filter': end_date_filter,
            'employee_group1s': employee_group1s,
            'employee_levels': employee_levels,
            'branch_id': branch_id,
        }