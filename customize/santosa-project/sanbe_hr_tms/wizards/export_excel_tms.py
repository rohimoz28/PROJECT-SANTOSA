import io
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import xlsxwriter
import logging
_logger = logging.getLogger(__name__)

class ExportExcelTms(models.TransientModel):
    _name = 'export.excel.tms'
    # _inherit = 'hr.tmsentry.summary'
    _description = 'Export Excel'

    # periode_id = fields.Many2one('hr.opening.closing', string='Periode ID', index=True)
    # department_id = fields.Many2one('hr.department', string='Sub Department')

    periode_id = fields.Many2one('hr.opening.closing', string='Periode ID', index=True)
    
    alldepartment = fields.Many2many('hr.department', 'hr_department_rel', string='All Department',  store=False)
    branch_id = fields.Many2one('res.branch', string='Branch', store=True, related="periode_id.branch_id",readonly=True)
    department_id = fields.Many2one(
        'hr.department',
        string='Sub Department',
        options="{'no_create': True}"
    )
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat', store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', store=True)
    

    @api.onchange('periode_id')
    def _onchange_periode_id(self):
        """Set branch_id and apply domain for department_id based on periode_id."""
        if self.periode_id:
            # Ambil branch_id dari periode_id
            self.branch_id = self.periode_id.branch_id.id
            # print(self.branch_id.id)
            # Ambil daftar department_id berdasarkan branch_id
            department_ids = self.env['hr.department'].search([
                ('branch_id', '=', self.branch_id.id)
            ]).ids

            # Logging daftar department_id
            _logger.info(f"Selected Periode ID: {self.periode_id.id}")
            # _logger.info(f"Branch ID: {self.branch_id.id}")
            _logger.info(f"List of Department IDs: {department_ids}")

            # Terapkan domain berdasarkan hasil pencarian
            return {
                # 'domain': {
                    'branch_id': self.branch_id.id
                # }
            }
            _logger.info(f"Branch ID: {self.branch_id.id}")
        else:
            # Reset branch_id dan department_id jika periode_id kosong
            self.branch_id = False
            self.department_id = False
            _logger.info("Branch ID and Department domain reset due to empty periode_id")
            return {
                'domain': {
                    'department_id': []
                }
            }

    def button_export_xlsx(self):
        self.ensure_one()
        
        tms_summary_domain = []
        if self.periode_id:
            tms_summary_domain.append(('periode_id', '=', self.periode_id.id))
        if self.department_id:
            tms_summary_domain.append(('department_id', '=', self.department_id.id))
        if self.directorate_id:
            tms_summary_domain.append(('directorate_id', '=', self.directorate_id.id))
        if self.division_id:
            tms_summary_domain.append(('division_id', '=', self.division_id.id))
        if self.hrms_department_id:
            tms_summary_domain.append(('hrms_department_id', '=', self.hrms_department_id.id))
        
        tms_summaries = self.env['hr.tmsentry.summary'].search(tms_summary_domain)
        
        if not tms_summaries:
            raise UserError(_("Tidak Ada Data Record Dari periode atau department yang dipilih"))
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.rekap_kehadiran_xls',
            'report_type': 'xlsx',
            'report_file': f'Rekap_Kehadiran_{self.periode_id.name or "All"}',
            'context': {
                'active_model': 'hr.tmsentry.summary',
                'active_ids': tms_summaries.ids,  # semua record
            }
        }
        


    def button_export_html(self):
        self.ensure_one()
        
        tms_summary_domain = []
        if self.periode_id:
            tms_summary_domain.append(('periode_id', '=', self.periode_id.id))
        if self.directorate_id:
            tms_summary_domain.append(('directorate_id', '=', self.directorate_id.id))
        if self.division_id:
            tms_summary_domain.append(('division_id', '=', self.division_id.id))
        if self.hrms_department_id:
            tms_summary_domain.append(('hrms_department_id', '=', self.hrms_department_id.id))
        
        tms_summaries = self.env['hr.tmsentry.summary'].search(tms_summary_domain)
        
        if not tms_summaries:
            raise UserError(_("Tidak Ada Data Record Dari periode atau department yang dipilih"))
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.report_attendance_html',  # <-- should match the `name` in <report>
            # 'report_name': 'sanbe_hr_tms.action_report_attendance',  # <-- should match the `name` in <report>
            'report_type': 'qweb-html',
            'report_file': f'Rekap_Kehadiran_{self.periode_id.name or "All"}',
            'context': {
                'active_model': 'hr.tmsentry.summary',
                'active_ids': tms_summaries.ids,
            }
        }


# re edits
    # def button_export_html(self):
    #     self.ensure_one()
        
    #     tms_summary_domain = []
    #     if self.periode_id:
    #         tms_summary_domain.append(('periode_id', '=', self.periode_id.id))
    #     if self.department_id:
    #         tms_summary_domain.append(('department_id', '=', self.department_id.id))
        
    #     tms_summaries = self.env['hr.tmsentry.summary'].search(tms_summary_domain)
        
    #     if not tms_summaries:
    #         raise UserError(_("Tidak Ada Data Record Dari periode atau department yang dipilih"))
        
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': 'sanbe_hr_tms.report_attendance_html',
    #         'report_type': 'qweb-html',
    #         'report_file': f'Rekap_Kehadiran_{self.periode_id.name or "All"}',
    #         'context': {
    #             'active_model': 'hr.tmsentry.summary',
    #             'active_ids': tms_summaries.ids,  # semua record
    #         }
    #     }
        
        
        
        # """
        # Generate HTML report based on selected filters
        
        # :return: Action for HTML report
        # """
        # self.ensure_one()
        
        # # Prepare domain for searching records
        # tms_summary_domain = []
        # if self.periode_id:
        #     tms_summary_domain.append(('periode_id', '=', self.periode_id.id))
        # if self.department_id:
        #     tms_summary_domain.append(('department_id', '=', self.department_id.id))
        
        # # Search for TMS summaries
        # tms_summaries = self.env['hr.tmsentry.summary'].search(tms_summary_domain)
        
        # if not tms_summaries:
        #     raise UserError(_("No Records Found for the Selected Period or Department"))
        
        # # Return report action
        # return self.env.ref('sanbe_hr_tms.action_report_attendance').report_action(tms_summaries)