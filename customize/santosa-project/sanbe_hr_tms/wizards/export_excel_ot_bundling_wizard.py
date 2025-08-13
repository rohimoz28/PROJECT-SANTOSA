from odoo.exceptions import UserError
from odoo import fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ExportExcelOvertimeBundling(models.TransientModel):
    _name = 'export.excel.ot.bundling'
    _description = 'Export Excel Overtime Bundling'

    branch_id = fields.Many2one('res.branch', string='Business Unit', tracking=True,  default=lambda self: self.env.user.branch_id)
    department_id = fields.Many2one(
        comodel_name ='hr.department',
        string ='Sub Department',
        domain =lambda self: self._get_departments_domain(),
        options = "{'no_create': True}"
    )
    directorate_id = fields.Many2one('sanhrms.directorate',string='Direktorat',  store=True)
    division_id = fields.Many2one('sanhrms.division',string='Divisi', store=True)
    hrms_department_id = fields.Many2one('sanhrms.department',
                                         string='Departemen', store=True)
    
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')


    # methods
    def _get_departments_domain(self):
        department_ids = self.env['sb.overtime.bundling'].search([]).mapped('department_id.id')
        return [('id', 'in', department_ids)] 

    def button_export_html(self):
        # This is a built-in Odoo method that ensures the method operates on a single record.
        self.ensure_one()

        ot_bundling_domain = []

        if self.department_id:
            ot_bundling_domain.append(('department_id', '=', self.department_id.id))
        if self.start_date:
            ot_bundling_domain.append(('req_date', '>=', self.start_date))
        if self.end_date:
            ot_bundling_domain.append(('req_date', '<=', self.end_date))

        ot_bundling = self.env['sb.overtime.bundling'].search(ot_bundling_domain)

        if not ot_bundling:
            raise UserError(_("Tidak Ada Data Record Dari department yang dipilih"))

        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.report_ot_bundling_html',
            'report_type': 'qweb-html',
            'report_file': f'Rekap_Overtime_{self.department_id.complete_name or "All"}',
            'context': {
                'active_model': 'sb.overtime.bundling',
                'active_ids': ot_bundling.ids  # semua record
            }
        }
    
    def button_export_export_xlsx(self):
        self.ensure_one()

        ot_bundling_domain = []
        if self.department_id:
            ot_bundling_domain.append(('department_id', '=', self.department_id.id))
        if self.start_date:
            ot_bundling_domain.append(('req_date', '>=', self.start_date))
        if self.end_date:
            ot_bundling_domain.append(('req_date', '<=', self.end_date))
        
        ot_bundling = self.env['sb.overtime.bundling'].search(ot_bundling_domain)
        
        if not ot_bundling:
            raise UserError(_("Tidak Ada Data Record Dari department yang dipilih"))
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'sanbe_hr_tms.report_ot_bundling_excel',
            'report_type': 'xlsx',
            'report_file': f'Rekap_Overtime_{self.department_id.complete_name or "All"}',
            'context': {
                'active_model': 'sb.overtime.bundling',
                'active_ids': ot_bundling.ids,  # semua record
            }
        }
