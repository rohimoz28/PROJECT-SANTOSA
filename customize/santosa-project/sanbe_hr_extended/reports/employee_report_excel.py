from odoo import models
import logging
_logger = logging.getLogger(__name__)


gender_map = {
    'male': 'Laki - laki',
    'female': 'Perempuan',
    'other': 'Lainnya'
}

class EmployeeReportExcel(models.AbstractModel):
    _name = 'report.sanbe_hr_extended.employee_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        try:
            # Logging context for debugging
            _logger.info(f"Context: {self.env.context}")
            
            if not lines:
                active_ids = self.env.context.get('active_ids', [])
                active_model = self.env.context.get('active_model', 'hr.employment.log')
                
                lines = self.env[active_model].browse(active_ids) if active_ids else []
            
            # Log total 
            _logger.info(f"Total lines retrieved: {len(lines)}")

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
                stype = (obj.service_type or '').upper()
                if stype in MUTATION_TYPES:
                    mutation_data = {
                        'no': index_mutation,
                        'nik': obj.employee_id.nik or '',
                        'name': obj.employee_id.name or '',
                        'job_id': obj.employee_id.job_id.name if obj.employee_id.job_id else '',
                        'service_type': stype,
                        'birthday': obj.employee_id.birthday or '',
                    }
                    mutation_lines.append(mutation_data)
                    index_mutation += 1 
                elif stype in EXIT_TYPES:
                    exit_data = {
                        'no': index_exit,
                        'nik': obj.employee_id.nik or '',
                        'name': obj.employee_id.name or '',
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
                        'nik': obj.employee_id.nik or '',
                        'name': obj.employee_id.name or '',
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

            # Formatting
            format_header = workbook.add_format({
                'font_size': 14,
                'bold': True,
                'align': 'center',
                'bg_color': '#F2F2F2',
                'border': 1
            })

            format_title = workbook.add_format({
                'font_size': 14,
                'bold': True,
                'align': 'center',

            })

            format_data = workbook.add_format({
                'font_size': 12,
                'align': 'left',
                'valign': 'vcenter',
                'border': 1
            })

            start_date = data.get('start_date_filter', '-')
            end_date = data.get('end_date_filter', '-')
            employee_group1s = data.get('employee_group1s', 'All')
            employee_levels = data.get('employee_levels', 'All')
            branch_id = data.get('branch_id', 'All')

            # Create worksheet
            sheet = workbook.add_worksheet("Employee Report")
            sheet.merge_range('A1:R1', f'LAPORAN KARYAWAN MASUK, KELUAR DAN MUTASI {branch_id}', format_header)
            row = 1

            sheet.merge_range('A2:B2', 'Periode: ', format_data)
            sheet.merge_range('C2:D2', f'{start_date} s/d {end_date}', format_data)
            row += 1

            sheet.merge_range('A3:B3', 'Payroll Group: ', format_data)
            sheet.merge_range('C3:D3', employee_group1s, format_data)
            row += 1

            sheet.merge_range('A4:B4', 'Level: ', format_data)
            sheet.merge_range('C4:D4', employee_levels, format_data)
            row += 2

            # KARYAWAN MASUK 
            sheet.write(row, 0, "KARYAWAN MASUK", format_title)
            row += 1
            headers_new = ["No", "Kode Bag", "NIK", "Nama", "Jabatan", "Tgl Lahir", "Jenis Kelamin", 
                        "No KTP", "Gaji", "Tgl Masuk", "Kontrak Kerja", "No Rekening", "THR (N/L)", 
                        "No NPWP", "Nama Atasan", "Jumlah Keluarga", "Pendidikan", "Keterangan"]
            for col, val in enumerate(headers_new):
                sheet.write(row, col, val, format_header)
            row += 1
            if new_lines:
                for rec in new_lines:
                    sheet.write(row, 0, rec['no'], format_data)
                    sheet.write(row, 1, '', format_data)
                    sheet.write(row, 2, rec['nik'], format_data)
                    sheet.write(row, 3, rec['name'], format_data)
                    sheet.write(row, 4, rec['job_id'], format_data)
                    sheet.write(row, 5, str(rec['birthday']), format_data)
                    sheet.write(row, 6, rec['gender'], format_data)
                    sheet.write(row, 7, rec['no_ktp'], format_data)
                    sheet.write(row, 9, str(rec['start_date']), format_data)
                    sheet.write(row, 10, rec['contract_id'], format_data)
                    sheet.write(row, 11, rec['bank_account_id'], format_data)
                    sheet.write(row, 12, '', format_data)
                    sheet.write(row, 13, rec['no_npwp'], format_data)
                    sheet.write(row, 15, '', format_data)
                    sheet.write(row, 14, rec['parent_id'], format_data)
                    sheet.write(row, 16, rec['title'], format_data)
                    sheet.write(row, 17, rec['service_type'], format_data)
                    row += 1
            else:
                sheet.merge_range(row, 0, row, len(headers_new)-1, "No Data Available", format_data)
                row += 1

            row += 1

            # KARYAWAN KELUAR
            sheet.write(row, 0, "KARYAWAN KELUAR", format_title)
            row += 1
            headers_exit = ["No", "Kode Bag", "NIK", "Nama", "Jabatan", "Tgl Lahir", "Jenis Kelamin", 
                            "No KTP", "Gaji", "Tgl Keluar", "Alasan Keluar", "Uang Pisah", "Keterangan"]
            for col, val in enumerate(headers_exit):
                sheet.write(row, col, val, format_header)
            row += 1
            if exit_lines:
                for rec in exit_lines:
                    sheet.write(row, 0, rec['no'], format_data)
                    sheet.write(row, 1, '', format_data)
                    sheet.write(row, 2, rec['nik'], format_data)
                    sheet.write(row, 3, rec['name'], format_data)
                    sheet.write(row, 4, rec['job_id'], format_data)
                    sheet.write(row, 5, str(rec['birthday']), format_data)
                    sheet.write(row, 6, rec['gender'], format_data)
                    sheet.write(row, 7, rec['no_ktp'], format_data)
                    sheet.write(row, 8, '', format_data)
                    sheet.write(row, 9, str(rec['start_date']), format_data)
                    sheet.write(row, 10, '', format_data)
                    sheet.write(row, 11, '', format_data)
                    sheet.write(row, 12, rec['service_type'], format_data)
                    row += 1
            else:
                sheet.merge_range(row, 0, row, len(headers_exit)-1, "No Data Available", format_data)
                row += 1

            row += 1

            # KARYAWAN MUTASI 
            sheet.write(row, 0, "KARYAWAN MUTASI", format_title)
            row += 1

            # FIRST HEADER
            sheet.merge_range(row, 0, row+1, 0, "No", format_header)
            sheet.merge_range(row, 1, row+1, 1, "Kode Bag", format_header)
            sheet.merge_range(row, 2, row+1, 2, "NIK", format_header)
            sheet.merge_range(row, 3, row+1, 3, "Nama", format_header)
            sheet.merge_range(row, 4, row+1, 4, "Jabatan", format_header)

            # MERGED HEADER
            sheet.merge_range(row, 5, row, 8, "Mutasi", format_header)
            sheet.write(row+1, 5, "Kode Bag Lama", format_header)
            sheet.write(row+1, 6, "Jabatan Lama", format_header)
            sheet.write(row+1, 7, "Kode Bag Baru", format_header)
            sheet.write(row+1, 8, "Jabatan Baru", format_header)

            # LAST HEADER
            sheet.merge_range(row, 9, row+1, 9, "Keterangan", format_header)

            row += 2

            if mutation_lines:
                for rec in mutation_lines:
                    sheet.write(row, 0, rec['no'], format_data)
                    sheet.write(row, 1, '', format_data)
                    sheet.write(row, 2, rec['nik'], format_data)
                    sheet.write(row, 3, rec['name'], format_data)
                    sheet.write(row, 4, rec['job_id'], format_data)
                    sheet.write(row, 5, '', format_data)
                    sheet.write(row, 6, '', format_data)
                    sheet.write(row, 7, '', format_data)
                    sheet.write(row, 8, '', format_data)
                    sheet.write(row, 9, rec['service_type'], format_data)
                    row += 1
            else:
                sheet.merge_range(row, 0, row, 9, "No Data Available", format_data)
                row += 1


        except Exception as e:
            _logger.error(f"Critical error in generate_xlsx_report: {e}")