from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class BundlingReportHTML(models.Model):
    _name = 'report.sanbe_hr_tms.report_ot_bundling_html'
    _description = 'HTML Bundling Report'


    @api.model
    def _get_report_values(self, docids, data=None):
        if not docids:
            active_ids = self.env.context.get('active_ids', [])
            active_model = self.env.context.get('active_model', 'sb.overtime.bundling')
            
            if not active_ids:
                raise UserError(_("Tidak Ada data untuk record"))
            
            lines = self.env[active_model].browse(active_ids)
            lines = lines.sorted(lambda o: o.no_request)
        else:
            lines = self.env['sb.overtime.bundling'].browse(docids)
            lines = lines.sorted(lambda o: o.no_request)


        # Prepare report data
        report_lines = []
        for index, obj in enumerate(lines, 1):
            try:
                # workingday = obj.employee_id.workingday or 0
                line_data = {
                    'no': index,
                    'branch_id': obj.branch_id.name or 'Tidak Diketahui', #BU
                    'department': obj.department_id.complete_name or 'Tidak Diketahui', #Department
                    'no_request': obj.no_request or 'Tidak Diketahui', #No Request
                    'req_date': obj.req_date or 'Tidak Diketahui', #Tanggal Request
                    'employee_id': obj.employee_id.name or None, #Employee
                    'nik': obj.nik or None, #NIK
                    'req_time_fr': self.float_to_time(obj.req_time_fr) or 0, #Req Time FR
                    'req_time_to': self.float_to_time(obj.req_time_to) or 0, #Req Time To
                    'approve_time_from': self.float_to_time(obj.approve_time_from) or 0, #Approve Time From
                    'approve_time_to': self.float_to_time(obj.approve_time_to) or 0, #Approve Time To
                    'rlz_time_fr': self.float_to_time(obj.rlz_time_fr) or 0, #Rel Time From
                    'rlz_time_to': self.float_to_time(obj.rlz_time_to) or 0, #Rel TIme To
                    'state': obj.state or None, #State
                    'periode_id': obj.periode_id.name or None
                    # 'delay_total': obj.delay_total or 0,
                    # 'delay_count': obj.delay_count or 0
                }
                
                report_lines.append(line_data)
                
            except Exception as e:
                # Log error but continue processing other records
                _logger.info(f"Error processing record: {e}")
        _logger.info(f"Processing row {index}: {report_lines}")
        return {
            'doc_model': 'sb.overtime.bundling',
            'docs': lines,
            'report_lines': report_lines,
        }
