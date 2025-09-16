from odoo import _, api, fields, models
import datetime
import logging
_logger = logging.getLogger(__name__)

class ReportEmpgroupXlsx(models.AbstractModel):
    _name = 'report.sanbe_hr_tms.rekap_empgroup_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        try:
            _logger.info(f"Context: {self.env.context}")

            # Get the latest value group record
            value = self.env['value.group'].search([], order='id desc', limit=1)
            _logger.info(f"Value group data: {value}")

            # Determine lines to process
            if not lines:
                active_ids = self.env.context.get('active_ids', [])
                # active_model = self.env.context.get('active_model', 'hr.employee')
                active_model = self.env.context.get('active_model', 'hr.empgroup.details')
                lines = self.env[active_model].browse(active_ids) if active_ids else []

            _logger.info(f"Total lines retrieved: {len(lines)}")

            # Workbook formatting
            format_header = workbook.add_format({
                'font_size': 12,
                'bold': True,
                'align': 'center',
                'bg_color': '#F2F2F2',
                'border': 1
            })

            format_data = workbook.add_format({
                'font_size': 10,
                'align': 'left',
                'valign': 'vcenter'
            })

            # Create worksheet
            sheet = workbook.add_worksheet("Employee Group Report")

            # Headers
            headers = [
                'Emp Group Name', 'Employee Name', 'NIK', 'Job Position', 
                'Working Day', 'Date From', 'Date To'
            ]
            col_widths = [len(header) for header in headers]

            # Write headers
            for col, header in enumerate(headers):
                sheet.write(0, col, header, format_header)

            # Check if lines is empty
            if not lines:
                sheet.write(1, 0, 'No data available', format_data)
                return

            # Process lines
            row = 1
            global_index = 1

            for obj in lines:
                # Skip employees with certain status
                if obj.emp_status not in ['confirmed', 'probation']:
                    _logger.info(f"Skipping employee {obj.name} with status {obj.emp_status}")
                    continue

                try:
                    # Get value_id and value_name for each row
                    current_value = self.env['value.group'].search([], order='id desc', limit=1)
                    
                    # Prepare row data
                    data_row = [
                        current_value.value_name or '',
                        obj.name or 'Tidak Diketahui',
                        obj.nik or 'Tidak Diketahui',
                        obj.job_id.name or 'Tidak Diketahui',
                        # obj.workingday or 0,
                        obj.wdcode or 'Tidak Diketahui',
                        obj.valid_from.strftime('%d-%m-%Y') ,
                        obj.valid_to.strftime('%d-%m-%Y') ,
                        # obj.wd_id.code or 'Tidak Diketahui',
                        # obj.wd_valid_from.strftime('%d-%m-%Y') ,
                        # obj.wd_valid_to.strftime('%d-%m-%Y') ,
                    ]

                    _logger.info(f"Processing row {data_row}")

                    # Write row data
                    for col, value in enumerate(data_row):
                        str_value = str(value)
                        sheet.write(row, col, value, format_data)
                        col_widths[col] = max(col_widths[col], len(str_value) + 2)

                    row += 1
                    global_index += 1

                except Exception as detail_error:
                    _logger.error(f"Error processing employee: {detail_error}")
                    sheet.write(row, 0, f"Error processing employee: {detail_error}", format_data)
                    row += 1
                    global_index += 1

            # Set column widths
            for col, width in enumerate(col_widths):
                sheet.set_column(col, col, min(width, 50))

        except Exception as e:
            _logger.error(f"Critical error in generate_xlsx_report: {e}")
            sheet = workbook.add_worksheet("Error")
            sheet.write(0, 0, f"Error generating report: {e}", format_data)