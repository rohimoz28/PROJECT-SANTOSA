from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class AttendanceReportHTML(models.AbstractModel):
    _name = 'report.sanbe_hr_tms.report_attendance_html'
    _description = 'HTML Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Prepare data for HTML report
        
        :param docids: List of record IDs
        :param data: Additional data passed from the report action
        :return: Dictionary of report values
        """
        # If no docids provided, try to get from context
        if not docids:
            active_ids = self.env.context.get('active_ids', [])
            active_model = self.env.context.get('active_model', 'hr.tmsentry.summary')
            
            if not active_ids:
                raise UserError(_("Tidak Ada data untuk record"))
            
            lines = self.env[active_model].browse(active_ids)
        else:
            lines = self.env['hr.tmsentry.summary'].browse(docids)

        # Prepare report data
        report_lines = []
        for index, obj in enumerate(lines, 1):
            try:
                workingday = obj.employee_id.workingday or 0
                line_data = {
                    'no': index,
                    'employee_name': obj.employee_id.name or 'Tidak Diketahui',
                    'employee_nik': obj.nik or 'Tidak Diketahui',
                    'job_title': obj.job_id.name or 'Tidak Diketahui',
                    'attendee_total': workingday,
                    'attendee_count': obj.attendee_count or 0,
                    'absent_count': obj.absent_count or 0,
                    'leave_count': obj.leave_count or 0,
                    'sick_count': obj.sick_count or 0,
                    'ot1_total': obj.ot1_totalx or 0,
                    'ot2_total': obj.ot2_totalx or 0,
                    'nightshift1_count': obj.nightshift_count or 0,
                    'nightshift2_count': obj.nightshift2_count or 0,
                    'state': obj.state or 'Tidak Diketahui',
                    'deduction': obj.is_deduction or 'Tidak Diketahui',
                    'delay_total': obj.delay_total or 0,
                    'delay_count': obj.delay_count or 0
                }
                
                report_lines.append(line_data)
                
            except Exception as e:
                # Log error but continue processing other records
                _logger.info(f"Error processing record: {e}")
        _logger.info(f"Processing row {index}: {report_lines}")
        return {
            'doc_model': 'hr.tmsentry.summary',
            'docs': lines,
            'report_lines': report_lines,
        }