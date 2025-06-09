from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ReportHonorXlsx(models.AbstractModel):
    _name = 'report.santosa_finance.rekap_honor_docter_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, lines):
        try:
            # Logging context for debugging
            _logger.info(f"Context: {self.env.context}")
            
            if not lines:
                active_ids = self.env.context.get('active_ids', [])
                active_model = self.env.context.get('active_model', 'santosa_finance.akun_kontrol_honor_dokter')
                
                lines = self.env[active_model].browse(active_ids) if active_ids else []
            
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
            sheet = workbook.add_worksheet("Kontrol Honor Dokter")
            sheet.merge_range('A1:K1', 'Rekap Honor Dokter', format_header)
            
                        # Headers
            headers = [
                'No', 'Penjamin Name', 'Trx Date', 'Trx No', 'Invoice No', 'No Trx Klaim', 'Piutang Klaim', 
                'Tolakan Klaim', 'Fee Dokter', 'Beban Biaya', 'Piutang Usaha'
            ]
                        # col_widths= max(len(header) + 2 for header in headers)
            col_widths= [len(headers)*1.5 for headers in headers]
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
                        obj.Penjaminid.name if obj.Penjaminid else 'Tidak Diketahui',
                        # obj.TrxDate or 'Tidak Diketahui',
                        obj.Invoice_date.strftime('%d/%m/%Y') if obj.Invoice_date else 'Tidak Diketahui',
                        obj.TrxNo or 'Tidak Diketahui',
                        obj.Invoice_No  or 'Tidak Diketahui',
                        obj.NoTrxKlaim or 0,
                        obj.PiutangKlaim or 0,
                        obj.TolakanKlaim or 0,
                        obj.FeeDokter or 0,
                        obj.BebanBiaya or 0,
                        obj.PiutangUsaha or 0
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