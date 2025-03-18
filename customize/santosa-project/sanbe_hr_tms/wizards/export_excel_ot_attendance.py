import io
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import xlsxwriter
import logging
_logger = logging.getLogger(__name__)

class ExportExcelOvertimeAttendance(models.TransientModel):
    _name = 'export.excel.ot.attendance'
    # _inherit = 'hr.tmsentry.summary'
    _description = 'Export Excel Overtime Request'

    department_id = fields.Many2one(
        'hr.department',
        string='Sub Department',
        domain=lambda self: self._get_departments_domain(),
        options="{'no_create': True}"
    )
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def _get_departments_domain(self):
        """
        Return the domain to filter departments based on the departments
        available in the sb.overtime.attendance model.
        """
        department_ids = self.env['sb.overtime.attendance'].search([]).mapped('department_id.id')
        return [('id', 'in', department_ids)]

    def button_export_html(self):
        self.ensure_one()
        
        ot_attendance_domain = []
        if self.department_id:
            ot_attendance_domain.append(('department_id', '=', self.department_id.id))
        if self.start_date:
            ot_attendance_domain.append(('req_date', '>=', self.start_date))
        if self.end_date:
            ot_attendance_domain.append(('req_date', '<=', self.end_date))

        ot_attendance = self.env['sb.overtime.attendance'].search(ot_attendance_domain)
        
        if not ot_attendance:
            raise UserError(_("Tidak Ada Data Record Dari department yang dipilih"))
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.report_ot_attendance_html',
            'report_type': 'qweb-html',
            'report_file': f'Rekap_Overtime_{self.department_id.complete_name or "All"}',
            'context': {
                'active_model': 'sb.overtime.attendance',
                'active_ids': ot_attendance.ids,  # semua record
            }
        }

    def button_export_xlsx(self):
        self.ensure_one()
        
        ot_attendance_domain = []
        if self.department_id:
            ot_attendance_domain.append(('department_id', '=', self.department_id.id))
        if self.start_date:
            ot_attendance_domain.append(('req_date', '>=', self.start_date))
        if self.end_date:
            ot_attendance_domain.append(('req_date', '<=', self.end_date))
        
        ot_attendance = self.env['sb.overtime.attendance'].search(ot_attendance_domain)
        
        if not ot_attendance:
            raise UserError(_("Tidak Ada Data Record Dari department yang dipilih"))
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.report_ot_attendance_excel',
            'report_type': 'xlsx',
            'report_file': f'Rekap_Overtime_{self.department_id.complete_name or "All"}',
            'context': {
                'active_model': 'sb.overtime.attendance',
                'active_ids': ot_attendance.ids,  # semua record
            }
        }