from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ReportKehadiranXlsx(models.AbstractModel):
    _name = 'report.sanbe_hr_tms.rekap_kehadiran_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        try:
            # Logging context for debugging
            _logger.info(f"Context: {self.env.context}")
            
            if not lines:
                active_ids = self.env.context.get('active_ids', [])
                active_model = self.env.context.get('active_model', 'hr.tmsentry.summary')
                
                lines = self.env[active_model].browse(active_ids) if active_ids else []
            
            # Log total 
            _logger.info(f"Total lines retrieved: {len(lines)}")

            # Formatting
            format_header = workbook.add_format({
                'font_size': 14,
                'bold': True,
                'align': 'center',
                'bg_color': '#F2F2F2',
                'border': 1
            })

            format_data = workbook.add_format({
                'font_size': 12,
                'align': 'left',
                'valign': 'vcenter'
            })

            # Create worksheet
            sheet = workbook.add_worksheet("Rekap Kehadiran")
            sheet.merge_range('A1:L1', 'Rekap Perhitungan Kehadiran dan Overtime - HRMS', format_header)

            # Headers
            headers = [
                'No', 'Nama Karyawan', 'NIK', 'Jabatan', 'Hari Kerja', 'Kehadiran', 
                'Mangkir', 'Total Izin', 'Total Sakit', 'Total OT1', 
                'Total OT2', 'Shift Malam 1', 'Shift Malam 2', 'Status', 'Potongan', 
                'Total Delay', 'Total Times Delay'
            ]

            # col_widths= max(len(header) + 2 for header in headers)
            col_widths= [len(headers) for headers in headers]

            # Write headers
            for col, header in enumerate(headers):
                sheet.write(2, col, header, format_header)

            # Write data
            row = 3
            if not lines:
                sheet.write(row, 0, 'Tidak ada data', format_data)
                return

            # Detailed logging
            _logger.info(f"Processing {len(lines)} lines")

            for index, obj in enumerate(lines, 1):
                try:
                    # Safely get values with error handling
                    data_row = [
                        index,
                        obj.employee_id.name if obj.employee_id else 'Tidak Diketahui',
                        obj.nik or 'Tidak Diketahui',
                        obj.job_id.name if obj.job_id else 'Tidak Diketahui',
                        obj.employee_id.workingday or 0,
                        obj.attendee_count or 0,
                        obj.absent_count or 0,
                        obj.leave_count or 0,
                        obj.sick_count or 0,
                        obj.ot1_totalx or 0,
                        obj.ot2_totalx or 0,
                        obj.nightshift_count or 0,
                        obj.nightshift2_count or 0,
                        obj.state or 'Tidak Diketahui',
                        obj.is_deduction or 'Tidak Diketahui',
                        obj.delay_total or 0,
                        obj.delay_count or 0
                    ]

                    # Logging each row for detailed debugging
                    _logger.info(f"Processing row {index}: {data_row}")

                    # Write row data and update column widths
                    for col, value in enumerate(data_row):
                        str_value = str(value)
                        sheet.write(row, col, value, format_data)
                        
                        # Update column width if needed
                        col_widths[col] = max(col_widths[col], len(str_value) + 2)

                    row += 1

                except Exception as row_error:
                    _logger.error(f"Error processing row {index}: {row_error}")

            # Set column widths
            for col, width in enumerate(col_widths):
                sheet.set_column(col, col, min(width, 50))

        except Exception as e:
            _logger.error(f"Critical error in generate_xlsx_report: {e}")
            