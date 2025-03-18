import time
from datetime import datetime
import tempfile
import binascii
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo import models, fields, exceptions, api, _, Command

from datetime import datetime


import logging
_logger = logging.getLogger(__name__)
import io
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class HrTMSEntryImportData(models.TransientModel):
    _name = 'hr.tmsimport.wiz'
    _description = 'TMS Import Wizard'

    file_import = fields.Binary(attachment=True,string='Select Excel File')
    file_name = fields.Char("File Name")
    tms_sync =  fields.Many2one('hr.tms.syncmachine',string='TMS Sync ID')
    @api.model
    def default_get(self, fields):
        result = super(HrTMSEntryImportData, self).default_get(fields)
        mysync = self._context.get('active_id')
        if mysync:
            result['tms_sync'] = mysync
        return result


    def action_import_data(self):
        mytmsentry = False
        for alldata in self:
            if not alldata.file_import:
                return
            alldata.tms_sync.write({'file_import': alldata.file_import,
                                    'file_name': alldata.file_name})
            mytmsentry = alldata.tms_sync
            try:
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file_import))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)

            except:
                raise UserError(_("Invalid file!"))
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or row.value,
                            sheet.row(row_no)))
                    absence_date = str(xlrd.xldate.xldate_as_datetime(float(line[0]),0)).split(' ')[0]
                    area1 = str(str(line[1])).split(' ')[1]
                    bid = '%s %s' %(str(line[5]).split(' ')[1],str(line[5]).split(' ')[2])
                    area_id = self.env['res.territory'].sudo().search([('name','=',area1)],limit=1)
                    branch_id = self.env['res.branch'].sudo().search([('name','=',str(line[2]))],limit=1)
                    employee_id = self.env['hr.employee'].sudo().search([('name','=',str(line[3]))],limit=1)
                    department_id = self.env['hr.department'].sudo().search([('name','=',bid)],limit=1)
                    job_id = self.env['hr.job'].sudo().search([('name','=',str(line[6]))],limit=1)
                    wd_id = self.env['hr.working.days'].sudo().search([('code','=',str(line[7]))],limit=1)
                    employee_group_id = self.env['hr.empgroup'].sudo().search([('code','=',wd_id.id)])
                    time_in = str(xlrd.xldate.xldate_as_datetime(float(line[8]),0)).split(' ')[1]
                    time_out = str(xlrd.xldate.xldate_as_datetime(float(line[9]),0)).split(' ')[1]
                    absence_status =  str(line[10])
                    if absence_status == 'Delay In':
                        absence_status = 'delay_in'
                    else:
                        absence_status = str(line[10]).lower()
                    self.env['hr.attendance'].sudo().create({'tmssync_id': alldata.tms_sync.id or alldata.tms_sync._origin.id,
                                                            'dates': absence_date,
                                                            'area_id': area_id.id,
                                                            'branch_id': branch_id.id,
                                                            'employee_id': employee_id.id,
                                                            'nik': str(line[4]),
                                                            'department_id': department_id.id,
                                                            'job_id': job_id.id,
                                                            'time_in': time_in,
                                                            'time_out': time_out,
                                                            'codes': employee_group_id.id,
                                                            'attendence_status': absence_status})
                    alldata.tms_sync.write({'state': 'done'})
                    alldata.tms_sync.env.cr.commit()
        if mytmsentry:
            return mytmsentry.action_view_tmsentry(mytmsentry.tmsentry_ids)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

