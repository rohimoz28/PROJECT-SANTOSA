# -*- coding : utf-8 -*-
###########################################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
############################################################################################################

import time
import tempfile
import binascii
import dateutil.parser
from datetime import date,datetime,time, timedelta
from odoo.exceptions import UserError
from odoo import models, fields, exceptions, api, _, Command
from odoo.modules.module import get_module_resource

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
#try:
#from idris import read_table,to_pandas_schema,read_schema,list_tables
from . import idris as mdb
#except ImportError:
#    _logger.debug('Cannot `import pandas_access`.')
#import pyodbc
#import jaydebeapi
from mdb_parser import MDBParser, MDBTable

import numpy as np
np.float_ = np.float64

#ucanaccess_jars = [
#    get_module_resource('sanbe_hr_tms', 'static/src/UCanAccess/ucanaccess-5.0.1.jar'),
#    get_module_resource('sanbe_hr_tms', 'static/src/UCanAccess/lib/commons-lang3-3.8.1.jar'),
#    get_module_resource('sanbe_hr_tms', 'static/src/UCanAccess/lib/commons-logging-1.2.jar'),
#    get_module_resource('sanbe_hr_tms', 'static/src/UCanAccess/lib/hsqldb-2.5.0.jar'),
#    get_module_resource('sanbe_hr_tms', 'static/src/UCanAccess/lib/jackcess-3.0.1.jar'),
#]

TMS_SYNC_STATE = [
    ('draft', 'Draft'),
    ('done', "Close"),
]

#def get_dbconn(file, password=None):
#    pyodbc.pooling = False
#    dbdsn = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' %(file)
#    # dbdsn = f'Driver={driver};Dbq={file};'
#    if password:
#        dbdsn += f'Pwd={password};'
#    return pyodbc.connect(dbdsn)

class HRTMSSyncMachine(models.TransientModel):
    _name = "hr.tms.syncmachine"
    _description = 'HR TMS Tarik Data Dari Machine'

    @api.depends('area_id')
    def _isi_semua_branch(self):
        for allrecs in self:
            databranch = []
            for allrec in allrecs.area_id.branch_id:
                mybranch = self.env['res.branch'].search([('name','=', allrec.name)], limit=1)
                databranch.append(mybranch.id)
            allbranch = self.env['res.branch'].sudo().search([('id','in', databranch)])
            allrecs.branch_ids =[Command.set(allbranch.ids)]

    transfer_from = fields.Selection([('import_file','Import File'),
                                      ('leave_module','Leave module'),
                                      ('absent_machine','Absent Machine')], default='import_file', string='Transfer From')
    state = fields.Selection(
        selection=TMS_SYNC_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    file_type= fields.Selection([('xls','XLS'),
                                 ('mdb','MDB')],string='File Type',default='mdb')
    file_import_mdb = fields.Binary(attachment=True,string='Select Access File To Import')
    file_import_xls = fields.Binary(attachment=True,string='Select Excel File To Import')
    file_name_xls = fields.Char("File Name Excel" ,readonly="state == 'done'")
    file_name_mdb = fields.Char("File Name Access" ,readonly="state == 'done'")
    machine_froms = fields.Many2one('hr.machine.setting',string='Machine From',tracking=True)
    machine_tos = fields.Many2one('hr.machine.setting',string='To',tracking=True)
    periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True)
    date_from = fields.Date(string='Date From',readonly="state == 'done'",related='periode_id.open_periode_from')
    date_to  = fields.Date(string='To',related='periode_id.open_periode_to')
    department_id = fields.Many2one('hr.department', string='Sub Department')
    employee_id = fields.Many2one('hr.employee', string='Employee')

    area_id = fields.Many2one('res.territory', string='Area ID', index=True)
    branch_ids = fields.Many2many('res.branch', 'res_branch_rel', string='AllBranch', compute='_isi_semua_branch')
    branch_id = fields.Many2one('res.branch', string='Business Units', index=True, domain="[('id','in',branch_ids)]")
    # tmsentry_ids = fields.Many2many('hr.attendance','rel_tmssync_id',auto_join=True )
    tmsummary_ids = fields.Many2many("hr.tmsentry.summary",'rel_hr_tms_syncmachine',auto_join=True )

    @api.depends('tmsentry_ids','state')
    def _get_tms_entry(self):
        #Search all data in tms entry ids and fill tmsentry_count and tmsentry_ids
        for order in self:
            myentry = self.env['hr.attendance'].sudo().search([('rel_hr_tms_syncmachine','=',order.id or order._origin.id)])
            order.tmsentry_ids = myentry.ids or []
            order.tmsentry_count = len(myentry)

    def process_data(self):
        return True

    def _getwaktu(self,waktu):
        ret = timedelta()
        for i in waktu:
            (h, m, s) = i.split(':')
            d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            ret += d
        return ret

    def _getwaktu2(self,waktu):
        ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m))
        ret += d
        return ret

    def _getwaktu3(self,waktu):
        #ret = timedelta()
        (h, m, s) = waktu.split(':')
        d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        ret = self._getfloat(d)
        return ret

    def ubahjam(self,waktu):
        hours, seconds = divmod(waktu * 3600, 3600)  # split to hours and seconds
        minutes, seconds = divmod(seconds, 60)
        #result = '{0:02.0f}:{1:02.0f}'.format(*divmod(waktu * 60, 60))
        result = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(hours, minutes, seconds)
        return result

    def _getjam(self,jam):
        ret = None
        detik = jam.total_seconds()
        hour = divmod(detik,3600)[0]
        sisad = detik - (hour * 3600)
        minute = divmod(sisad,60)[0]
        second = sisad - (minute * 60)
        ret = str(hour) + ":" + minute + ":" + second
        return ret

    def _getfloat(self, jam):
        ret = None
        detik = jam.total_seconds()
        hour = divmod(detik,3600)[0]
        minute = divmod(detik,3600)[1]/3600
        ret = hour + minute
        return ret

    def import_data(self):
        for alldata in self:
            tmsdata = []
            emp_id_data = []
            # print(">>>>>>>>>>>>>>>")
            # print("self = ", self.read())
            # print(">>>>>>>>>>>>>>>")
            # raise UserError("ok")

            if alldata.file_type == 'mdb':
                if not alldata.file_import_mdb:
                    raise UserWarning("Please Select MS ACCESS File To Import First!")
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".mdb")
                #fp = tempfile.NamedTemporaryFile(delete= False,suffix=".mdb")
                fp.write(binascii.a2b_base64(self.file_import_mdb))
                fp.seek(0)
                #try:
                #    classpath = ":".join(ucanaccess_jars)
                #    cnxn = jaydebeapi.connect(
                #        "net.ucanaccess.jdbc.UcanaccessDriver",
                #        f"jdbc:ucanaccess://{fp.name};newDatabaseVersion=V2010",
                #        ["", ""],
                #        classpath
                #        )
                #except:
                #    pass
                #    raise UserError("Error Connection")
                #
                #crsr = cnxn.cursor()
                #SQL2 = """
                #    SELECT B.Badgenumber, format(A.CHECKTIME, "YYYY/mm/dd") AS tgl, format(A.CHECKTIME, "YYYY/mm/dd") AS tglmasuk, (select MIN(FORMAT(C.CHECKTIME, 'hh:mm:ss')) FROM CHECKINOUT C WHERE format(C.CHECKTIME, "YYYY/mm/dd") = format(A.CHECKTIME, "YYYY/mm/dd") AND C.USERID = A.USERID AND C.CHECKTYPE='I') AS masuk,
                #    (IIF(
                #        (select MAX(FORMAT(D.CHECKTIME, 'hh:mm:ss'))
                #            FROM CHECKINOUT D
                #            WHERE format(D.CHECKTIME, "YYYY/mm/dd") = format(A.CHECKTIME, "YYYY/mm/dd")
                #                AND D.USERID = A.USERID AND D.CHECKTYPE='O') >=
                #        (select MIN(FORMAT(E.CHECKTIME, 'hh:mm:ss'))
                #        FROM CHECKINOUT E
                #        WHERE format(E.CHECKTIME, "YYYY/mm/dd") = format(A.CHECKTIME, "YYYY/mm/dd")
                #            AND E.USERID = A.USERID AND E.CHECKTYPE='I'),
                #        format(A.CHECKTIME, "YYYY/mm/dd"),
                #    FORMAT(DATEADD('d',A.CHECKTIME,1),'YYYY/MM/DD')
                #    )) AS tglout,
                #    (IIF(
                #        (select MAX(FORMAT(D.CHECKTIME, 'hh:mm:ss'))
                #            FROM CHECKINOUT D
                #            WHERE format(D.CHECKTIME, "YYYY/mm/dd") = format(A.CHECKTIME, "YYYY/mm/dd")
                #                AND D.USERID = A.USERID AND D.CHECKTYPE='O') >
                #        (select MIN(FORMAT(E.CHECKTIME, 'hh:mm:ss'))
                #        FROM CHECKINOUT E
                #        WHERE format(E.CHECKTIME, "YYYY/mm/dd") = format(A.CHECKTIME, "YYYY/mm/dd")
                #            AND E.USERID = A.USERID AND E.CHECKTYPE='I'),
                #        (select MAX(FORMAT(F.CHECKTIME, 'hh:mm:ss'))
                #        FROM CHECKINOUT F
                #        WHERE format(F.CHECKTIME, "YYYY/mm/dd") = format(A.CHECKTIME, "YYYY/mm/dd")
                #            AND F.USERID = A.USERID AND F.CHECKTYPE='O'),
                #    (select MAX(FORMAT(G.CHECKTIME, 'hh:mm:ss'))
                #        FROM CHECKINOUT G
                #        WHERE format(G.CHECKTIME, "YYYY/mm/dd") = FORMAT(DATEADD('d',A.CHECKTIME,1),'YYYY/MM/DD')
                #        AND G.USERID = A.USERID AND G.CHECKTYPE='O')
                #    )) AS keluar
                #    FROM CHECKINOUT AS A LEFT JOIN USERINFO AS B ON A.USERID = B.USERID
                #    GROUP BY A.USERID, B.Badgenumber, format(A.CHECKTIME, "YYYY/mm/dd"),FORMAT(DATEADD('d',A.CHECKTIME,1),'YYYY/MM/DD') ;
                #"""
                #SQL = """
                #    SELECT B.Badgenumber,
                #        format(A.CHECKTIME, "YYYY/mm/dd") AS tgl,
                #        A.CHECKTIME AS checktime,
                #        A.CHECKTYPE AS checktype
                #    FROM CHECKINOUT AS A
                #    LEFT JOIN USERINFO AS B ON A.USERID = B.USERID;
                #"""
                ## your query goes here
                ##crsr.PreparedStatement()
                #crsr.execute(SQL)
                #rex = crsr.fetchall()
                self._cr.execute("""delete from data_dbf_checkinout where user_id={_user_id}""".format(_user_id=self.env.user.id))
                self._cr.execute("""delete from data_dbf_userinfo where user_id={_user_id}""".format(_user_id=self.env.user.id))
                self._cr.execute("""delete from data_dbf where user_id={_user_id}""".format(_user_id=self.env.user.id))
                dbf_checkinout = self.env['data.dbf.checkinout'].sudo()
                dbf_userinfo = self.env['data.dbf.userinfo'].sudo()
                dbf = self.env['data.dbf'].sudo()

                format = "%Y-%m-%d %H:%M:%S.%f"
                format2 = "%Y-%m-%d"

                db_filename = fp.name
                db_att = mdb.read_table(db_filename, "CHECKINOUT")

                for aa in db_att.T.to_dict().values():
                    data_att = {
                        'userid' : aa['USERID'],
                        'checktime' : (dateutil.parser.parse(aa['CHECKTIME'])),
                        'checktype' : aa['CHECKTYPE'],
                        'user_id':self.env.user.id,
                        'tgl' : (dateutil.parser.parse(aa['CHECKTIME'])).strftime(format2),
                    }
                    rs = dbf_checkinout.create(data_att)

                db_user = mdb.read_table(db_filename, "USERINFO")
                acc_user = []
                #cdb_user = db_user.get_dataframe(infer_with_pandas=False)
                for bb in db_user.T.to_dict().values():
                    data_user = {
                        'userid' : bb['USERID'],
                        'badgenumber' : bb['Badgenumber'],
                        'name' : bb['Name'],
                        'user_id':self.env.user.id,
                    }
                    rs = dbf_userinfo.create(data_user)

                #print('+++++++++++++++++++++++++++')
                #db_att = MDBTable(file_path=fp.name, table="CHECKINOUT")
                #db_user = MDBTable(file_path=fp.name, table="USERINFO")

                sql = """SELECT b.badgenumber as badges_number,(att.tgl), 
                            att.tgl as tgl_masuk,
                            (select min(c.checktime::time) 
                                    from data_dbf_checkinout c 
                                    where att.userid = c.userid 
                                        and c.tgl = att.tgl and c.checktype='I' limit 1) jam_masuk,
                            (case when (select max(c.checktime::time) 
                                    from data_dbf_checkinout c 
                                    where att.userid = c.userid
                                        and c.tgl = att.tgl+1 and c.checktype='O' limit 1) <= 
                                    (select min(c.checktime::time) 
                                    from data_dbf_checkinout c 
                                    where c.userid = att.userid 
                                        and c.tgl = (att.tgl) and c.checktype='I' limit 1)
                                    then (att.tgl)+1
                                    else
                                        (case when (select max(c.checktime::time) 
                                        from data_dbf_checkinout c 
                                        where c.userid = att.userid 
                                            and c.tgl = (att.tgl) and c.checktype='O' limit 1) <= 
                                        (select min(c.checktime::time) 
                                        from data_dbf_checkinout c 
                                        where c.userid = att.userid 
                                            and c.tgl = (att.tgl)-1 and c.checktype='I' limit 1)
                                        then null
                                        else (att.tgl)
                                        end)
                                    end) tgl_keluar,
                            (case when (select max(c.checktime::time) 
                                    from data_dbf_checkinout c 
                                    where c.userid = att.userid 
                                        and c.tgl = (att.tgl)+1 and c.checktype='O' limit 1) <= 
                                    (select min(c.checktime::time) 
                                    from data_dbf_checkinout c 
                                    where c.userid = att.userid 
                                        and c.tgl = (att.tgl) and c.checktype='I' limit 1)
                                    then (select max(c.checktime::time) 
                                    from data_dbf_checkinout c 
                                    where c.userid = att.userid 
                                        and c.tgl = (att.tgl)+1 and c.checktype='O' limit 1)
                                    else 
                                        (case when (select max(c.checktime::time) 
                                        from data_dbf_checkinout c 
                                        where c.userid = att.userid 
                                            and c.tgl = (att.tgl) and c.checktype='O' limit 1) <= 
                                        (select min(c.checktime::time) 
                                        from data_dbf_checkinout c 
                                        where c.userid = att.userid 
                                            and c.tgl = (att.tgl)-1 and c.checktype='I' limit 1)
                                        then null
                                        else (select max(c.checktime::time) 
                                        from data_dbf_checkinout c 
                                        where c.userid = att.userid 
                                            and c.tgl = (att.tgl) and c.checktype='O' limit 1)
                                        end)
                                    end) jam_keluar
                        from data_dbf_checkinout att
                        left join data_dbf_userinfo b on b.userid = att.userid
                        group by b.badgenumber,att.userid,att.tgl
                        order by b.badgenumber,att.userid,att.tgl
                    """
                self._cr.execute(sql)
                hasil = self._cr.dictfetchall()

                for hsl in hasil:
                    myemp = self.env['hr.machine.details'].sudo().search([('name','=',hsl.get('badges_number')),('employee_id','!=',False)],limit=1)
                    if myemp:
                        #mycaritms = self.env['hr.attendance'].sudo().search([('dates','=',hsl.get('tgl')),('employee_id','=',myemp.employee_id.id),('periode_id','=',alldata.periode_id.id)],limit=1)
                        #mycaritms = self.env['data.upload.attendance'].sudo().search([('tgl','=',hsl.get('tgl')),('employee_id','=',myemp.employee_id.id),('periode_id','=',alldata.periode_id.id)],limit=1)
                        mycaritms = self.env['data.upload.attendance'].sudo().search([('tgl','=',hsl.get('tgl')),('employee_id','=',myemp.employee_id.id)],limit=1)
                        att_status = False
                        if hsl.get('jam_masuk') and hsl.get('jam_keluar'):
                            att_status = 'attendee'
                        if hsl.get('jam_masuk') is not None:
                            print('++++++++++++++++++')
                            print('jam masuk',str(hsl.get('jam_masuk')))
                            test = self._getwaktu3(str(hsl.get('jam_masuk')))
                            print('jam masuk konversi',test)
                            test2 = self.ubahjam(test)
                            print('konversi diubah lg ke waktu',test2)
                            print('++++++++++++++++++')
                        if mycaritms:
                            if hsl.get('jam_masuk') is not None or hsl.get('jam_keluar') is not None:
                                mycaritms.write({
                                    'time_in': self._getwaktu3(str(hsl.get('jam_masuk'))),
                                    'tgl_masuk': hsl.get('tgl_masuk'),
                                    'time_out': self._getwaktu3(str(hsl.get('jam_keluar'))),
                                    'tgl_keluar':hsl.get('tgl_keluar'),
                                    'tgl':hsl.get('tgl'),
                                    'attendence_status':att_status,
                                    #'periode_id' : alldata.periode_id.id,
                                    'badges_number' : hsl.get('badges_number'),
                                    'employee_id' : myemp.employee_id.id,
                                    'nik' : myemp.employee_id.nik,
                                    'user_id' : self.env.user.id,
                                    'state' : 'draft'
                                })
                        else:
                            if hsl.get('jam_masuk') is not None or hsl.get('jam_keluar') is not None:
                                mycaritms.create({
                                    'time_in': self._getwaktu3(str(hsl.get('jam_masuk'))),
                                    'tgl_masuk': hsl.get('tgl_masuk'),
                                    'time_out': self._getwaktu3(str(hsl.get('jam_keluar'))),
                                    'tgl_keluar':hsl.get('tgl_keluar'),
                                    'tgl':hsl.get('tgl'),
                                    'attendence_status':att_status,
                                    #'periode_id' : alldata.periode_id.id,
                                    'badges_number' : hsl.get('badges_number'),
                                    'employee_id' : myemp.employee_id.id,
                                    'nik' : myemp.employee_id.nik,
                                    'user_id' : self.env.user.id,
                                    'state' : 'draft'
                                })

                #crsr.close()
                #cnxn.close()
            elif alldata.file_type == 'xls':
                # print(">>>>>>>>>>>>>>>")
                # print("file_type = ",alldata.file_type)
                # print("file_import_xls = ",alldata.file_import_xls)
                # print(">>>>>>>>>>>>>>>")
                # else:
                # if not alldata.file_import_xls:
                #     raise UserWarning("Please Select Excel File To Import First!")
                try:
                    fp = tempfile.NamedTemporaryFile(delete= False, suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.file_import_xls))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)

                except xlrd.biffh.XLRDError as e:
                    raise UserError(_(f"Error processing Excel file: {str(e)}"))
                except Exception as e:
                    raise UserError(_(f"Unexpected error: {str(e)}"))
                finally:
                    fp.close()  # Ensure file is closed even on exceptions

                emp_ids = False
                headers = [str(cell.value) for cell in sheet.row(0)]
                lst = [(x.lower()).replace(' ', '') for x in headers]
                pdate = lst.index('date')
                pnik = lst.index('nik')
                ptin = lst.index('timein')
                ptout = lst.index('timeout')
                ptglin = lst.index('tglin')
                ptglout = lst.index('tglout')

                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no == 0:
                        fields = [cell.value.encode('utf-8') for cell in sheet.row(row_no)]
                    else:
                        line = list(
                            map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or row.value,
                                sheet.row(row_no)))
                        # print('==============')
                        # print(pnik)
                        # print(str(int(line[pnik])))
                        # print('==============')
                        absence_date = str(xlrd.xldate.xldate_as_datetime(float(line[pdate]), 0)).split(' ')[0]
                        myemployee = self.env['hr.employee'].sudo().search([
                            ('nik', '=', line[pnik]),
                            ('state', '=', 'approved')
                        ])

                        myemp = self.env['hr.machine.details'].sudo().search([('employee_id', '=', myemployee.id)], limit=1)
                        if myemp:
                            badgenos = myemp.name
                        else:
                            badgenos = False

                        if isinstance(line[ptin], str) and line[ptin].strip() == "":
                            time_in = None
                        elif isinstance(line[ptin], (int, float)):
                            time_in = str(xlrd.xldate.xldate_as_datetime(float(line[ptin]), 0)).split(' ')[1]
                        else:
                            time_in = None

                        if isinstance(line[ptout], str) and line[ptout].strip() == "":
                            time_out = None  # Assign None if the cell is an empty string
                        elif isinstance(line[ptout], (int, float)):
                            # Process the value as a float and convert it to the desired time format
                            time_out = str(xlrd.xldate.xldate_as_datetime(float(line[ptout]), 0)).split(' ')[1]
                        else:
                            time_out = None  # Handle any other cases by assigning None

                        if isinstance(line[ptglin], (int, float)):
                            # If the value is a float or integer, treat it as an Excel serial date
                            tgl_in = xlrd.xldate.xldate_as_datetime(line[ptglin], 0).strftime('%Y-%m-%d')
                        elif isinstance(line[ptglin], str):
                            # # If the value is a string, assume it's in 'dd/mm/yyyy' format
                            # if line[ptglin].strip() == "":
                            #     tgl_in = None  # Assign None for empty strings
                            # else:
                            #     # If the value is a non-empty string, assume it's in 'dd/mm/yyyy' format
                            tgl_in = datetime.strptime(line[ptglin], '%d/%m/%Y').strftime('%Y-%m-%d')
                        else:
                            # Handle unexpected types
                            tgl_in = 'Invalid Date'

                        if isinstance(line[ptglout], (int, float)):
                            # If the value is a float or integer, treat it as an Excel serial date
                            tgl_out = xlrd.xldate.xldate_as_datetime(line[ptglout], 0).strftime('%Y-%m-%d')
                        elif isinstance(line[ptglout], str):
                            # if line[ptglin].strip() == "":
                            #     tgl_in = None  # Assign None for empty strings
                            # else:
                            # If the value is a string, assume it's in 'dd/mm/yyyy' format
                            tgl_out = datetime.strptime(line[ptglout], '%d/%m/%Y').strftime('%Y-%m-%d')
                        else:
                            # Handle unexpected types
                            tgl_out = 'Invalid Date'

                        nik = line[pnik]
                        att_status = 'attendee'
                        area_id = myemployee.area.id
                        branch_id = myemployee.branch_id.id

                        mycaritms = self.env['data.upload.attendance'].sudo().search([
                            ('tgl', '=', absence_date),
                            ('employee_id', '=', myemployee.id)
                        ], limit=1)

                        if myemployee:
                            status = 'register'
                        else:
                            status = 'unregister'

                        if time_in or time_out:
                            data = {
                                'time_in': self._getwaktu3(str(time_in)) if time_in else None,
                                'tgl_masuk': tgl_in,
                                'time_out': self._getwaktu3(str(time_out)) if time_out else None,
                                'tgl_keluar': tgl_out,
                                'tgl': absence_date,
                                'attendence_status': att_status,
                                'badges_number': badgenos,
                                'employee_id': myemployee.id,
                                'nik': nik,
                                'user_id': self.env.user.id,
                                'state': status,
                                'area_id': area_id,
                                'branch_id': branch_id,
                            }
                            # import pdb
                            # pdb.set_trace()

                            if mycaritms:
                                mycaritms.sudo().write(data)
                            else:
                                mycaritms.sudo().create(data)

                        emp_ids = myemployee.id if myemployee else False

            return alldata.action_view_tmsentry()

    def action_view_tmsentry(self, tmsdetails=False):
        # View for tms entry
        if not tmsdetails:
            # if no data then search for data in tms sync with mapped data tmsentry_id
            tmsdetails = self.mapped('tmsummary_ids')
        # action will be given from sanbe_hr_tms.action_hr_tmsentry
        action = self.env['ir.actions.actions']._for_xml_id('sanbe_hr_tms.action_hr_tmsentry_summary')
        if len(tmsdetails) > 1:
            # if data count in tms details greater than 1 then put the domain with the tmsdetailsids
            action['domain'] = [('id', 'in', tmsdetails.ids)]
        elif len(tmsdetails) == 1:
            # if data count in tms details is equal to 1 then open the form
            form_view = [(self.env.ref('sanbe_hr_tms.hr_tmsentry_summary_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tmsdetails.id
        else:
            # else we closed it
            action = {'type': 'ir.actions.act_window_close'}
        # lets open the view eg tree with domain or form view
        return action

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ('tree', 'form'):
            group_name = self.env['res.groups'].search([('name','=','HRD CA')])
            cekgroup = self.env.user.id in group_name.users.ids
            if cekgroup:
                for node in arch.xpath("//field"):
                    node.set('readonly', 'True')
                for node in arch.xpath("//button"):
                    node.set('invisible', 'True')
        return arch, view

class DataDbf(models.TransientModel):
    _name = "data.dbf"

    badges_number = fields.Char('Badges Number')
    tgl = fields.Date('Tgl Data')
    checktime = fields.Datetime('Check Time')
    checktype = fields.Char('Check Type')
    user_id = fields.Many2one('res.users',string='User')

class DataDbfCheckinOut(models.TransientModel):
    _name = "data.dbf.checkinout"

    userid = fields.Char('User Mesin')
    tgl = fields.Date('Tgl')
    checktime = fields.Datetime('Check Time')
    checktype = fields.Char('Check Type')
    user_id = fields.Many2one('res.users',string='User')

class DataDbfUserInfo(models.TransientModel):
    _name = "data.dbf.userinfo"

    userid = fields.Char('User Mesin')
    badgenumber = fields.Char('Badges Number')
    name = fields.Char('Name')
    user_id = fields.Many2one('res.users',string='User')

class DataTblUploadanAttendance(models.Model):
    _name = "data.upload.attendance"
    _description = 'HR TMS Data Upload Attendance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True)
    date_from = fields.Date(string='Date From',related='periode_id.open_periode_from')
    date_to = fields.Date(string='To',related='periode_id.open_periode_to')
    badges_number = fields.Char('Badges Number')
    nik = fields.Char('NIK')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    # area_id = fields.Many2one('res.territory',string='Area ID', related='employee_id.area', index=True )
    # branch_id = fields.Many2one('res.branch',string='Bisnis Unit',index=True,related='employee_id.branch_id')
    area_id = fields.Many2one('res.territory',string='Area')
    branch_id = fields.Many2one('res.branch',string='Business Unit')
    department_id = fields.Many2one('hr.department',string='Sub Department')
    tgl = fields.Date('Tgl Data')
    user_id = fields.Many2one('res.users',string='User')
    time_in = fields.Float('Time In')
    time_out = fields.Float('Time Out')
    tgl_masuk = fields.Date(string='Date In')
    tgl_keluar = fields.Date(string='Date Out')
    attendence_status = fields.Selection([('attendee','Attendee'),
                                          ('sick','Sick'),
                                          ('absent','Absent'),
                                          ('delay_in','Delay In'),
                                          ('leave','Leave'),
                                          ('outstation','OutStation')],string='Attendence Status')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('sync', 'Sync'),
        ('register', 'Terdaftar'),
        ('unregister', 'Tidak Terdaftar'),
        ('resync', 'Re-Sync')
    ],string='State', tracking=True)
    date_sync = fields.Date('Tgl Sync', tracking=True)
    date_resync = fields.Date('Tgl Re-Sync', tracking=True)

    def sync_data(self):
        sel_ids = self.env.context.get('active_ids', [])
        sel_rec = self.env['data.upload.attendance'].browse(sel_ids)
        # print(">>>>>>>>>>>>>>>>")
        # print("sel_ids= ", sel_ids)
        # print("sel_record= ", sel_rec)
        # print("self= ", self)
        # print(">>>>>>>>>>>>>>>>")

        # data_upload_attendance
        # bandingkan dengan sb_tmsentry_details
        # jika di sb_tmsentry_details ada tanggalnya, tapi di data_upload_attendance tidak ada, maka tidak hadir

        for data in sel_rec:
            tmsentry_detail = self.env['sb.tms.tmsentry.details'].sudo().search([
                ('employee_id', '=', data.employee_id.id),
                ('details_date', '=', data.tgl)
            ])
            vals = {
                'date_in': data.tgl_masuk,
                'time_in': data.time_in,
                'date_out': data.tgl_keluar,
                'time_out': data.time_out,
                'status_attendee': data.attendence_status,
            }

            # If the detail record exists, update it
            if tmsentry_detail:
                tmsentry_detail.sudo().write(vals)
                rec_state = 'register'
            else:  # If not, consider creating or updating the status
                tmsentry_detail.sudo().create(vals)  # Assuming you meant to create a new record here
                rec_state = 'unregister'

            # Update the `rec` fields
            data.state = rec_state
            data.date_sync = fields.Date.today()

            # Commit the transaction (if necessary)
            data.env.cr.commit()

        # for rec in sel_rec:
        #     cemp = self.env['hr.attendance'].sudo().search([
        #         ('employee_id', '=', rec.employee_id.id),
        #         ('dates', '=', rec.tgl)
        #     ])
        #     if cemp:
        #         cemp.sudo().write({
        #             'tgl_masuk': rec.tgl_masuk,
        #             'time_in': rec.time_in,
        #             'tgl_keluar': rec.tgl_keluar,
        #             'time_out': rec.time_out,
        #             'attendence_status': rec.attendence_status,
        #         })
        #         rec.state = 'register'
        #         rec.date_sync = fields.Date.today()
        #         rec.env.cr.commit()

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type in ('tree', 'form'):
            for node in arch.xpath("//field"):
                node.set('readonly', 'True')
            for node in arch.xpath("//tree"):
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')
            for node in arch.xpath("//form"):
                node.set('create', '0')
        return arch, view

    def resync_data(self):
        sel_ids = self.env.context.get('active_ids', [])
        sel_recx = self.env['data.upload.attendance'].browse(sel_ids)
        sel_rec = sel_recx.filtered(lambda p: p.state=='sync')
        for rec in sel_rec:
            cemp = self.env['hr.attendance'].sudo().search([('employee_id','=',rec.employee_id.id),
                                                            ('dates','=',rec.tgl)])
            if cemp:
                cemp.sudo().write({
                    'tgl_masuk': rec.tgl_masuk,
                    'time_in': rec.time_in,
                    'tgl_keluar': rec.tgl_keluar,
                    'time_out': rec.time_out,
                    'attendence_status': rec.attendence_status,
                })
                rec.state = 'resync'
                rec.date_resync = fields.Date.today()
                rec.env.cr.commit()

    def import_data2(self):
        for alldata in self:
            tmsdata = []
            emp_id_data = []

            if alldata.file_type == 'mdb':
                if not alldata.file_import_mdb:
                    raise UserWarning("Please Select MS ACCESS File To Import First!")
                fp = tempfile.NamedTemporaryFile(delete= False,suffix=".accdb")
                #fp = tempfile.NamedTemporaryFile(delete= False,suffix=".mdb")
                fp.write(binascii.a2b_base64(self.file_import_mdb))
                fp.seek(0)
                conn = get_dbconn(fp.name)
                curs = conn.cursor()
                # connect to db
                SQL = 'SELECT uinf.Badgenumber,inout.CHECKTIME, inout.CHECKTYPE FROM CHECKINOUT inout LEFT JOIN USERINFO uinf ON inout.USERID = uinf.USERID'  # your query goes here
                rows = curs.execute(SQL).fetchall()
                curs.close()
                conn.close()
                cntin = 0
                cntout = 0
                for allrows in rows:
                    myemp = self.env['hr.machine.details'].sudo().search([('name','=',allrows.Badgenumber),('employee_id','!=',False)],limit=1)
                    if myemp:
                        tglcheck = allrows.CHECKTIME.strftime('%Y/%m/%d')
                        mycaritms = self.env['hr.attendance'].sudo().search([('employee_id','=',myemp.employee_id.id),('dates','=',tglcheck),('periode_id','=',alldata.periode_id.id)])
                        if mycaritms:
                            timeins = allrows.CHECKTIME.strftime('%H:%M:%S')
                            if allrows.CHECKTYPE == 'I':
                                mycaritms.write({'time_in': timeins})
                            else:
                                mycaritms.write({'time_out': timeins})
            else:
                if not alldata.file_import_xls:
                    raise UserWarning("Please Select Excel File To Import First!")
                try:
                    fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.file_import_xls))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)

                except:
                    raise UserError(_("Invalid file!"))
                emp_ids = False
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(
                            map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or row.value,
                                sheet.row(row_no)))
                        absence_date = str(xlrd.xldate.xldate_as_datetime(float(line[0]),0)).split(' ')[0]
                        myemployee = self.env['hr.employee'].sudo().search([('nik','=',str(line[1]))])
                        # employee_group_id = self.env['hr.empgroup'].sudo().search([('code','=',line[7])])
                        time_in = str(xlrd.xldate.xldate_as_datetime(float(line[2]),0)).split(' ')[1]
                        time_out = str(xlrd.xldate.xldate_as_datetime(float(line[3]),0)).split(' ')[1]
                        mycaritms = self.env['hr.attendance'].sudo().search(
                            [('employee_id', '=', myemployee.id), ('dates', '=', absence_date),
                             ('periode_id', '=', alldata.periode_id.id)])
                        if mycaritms:
                            mycaritms.write({
                                'time_in': time_in,
                                'time_out': time_out,
                            })
                        emp_ids = myemployee.id
                return alldata.action_view_tmsentry()
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _('Import TMS Entry - Data'),
        #     'res_model': 'hr.tmsimport.wiz',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'context': {'active_id': self.id},
        #     'views': [[False, 'form']]
        # }


class DataTblUploadanAtt(models.Model):
    _name = "data.upload.attendace"

    periode_id = fields.Many2one('hr.opening.closing',string='Periode ID',index=True)
    date_from = fields.Date(string='Date From',related='periode_id.open_periode_from')
    nik = fields.Char('Nik')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    tgl = fields.Date('Tgl Data')
    checktime = fields.Datetime('Check Time')
    checktype = fields.Char('Check Type')
    #checktime = fields.Datetime('Check Time')
    #checktype = fields.Char('Check Type')
    user_id = fields.Many2one('res.users',string='User')
    time_in = fields.Float('Time In')
    time_out = fields.Float('Time Out')
    tgl_masuk = fields.Date(string='Date In')
    tgl_keluar = fields.Date(string='Date Out')
    attendence_status = fields.Selection([('attendee','Attendee'),
                                          ('sick','Sick'),
                                          ('absent','Absent'),
                                          ('delay_in','Delay In'),
                                          ('leave','Leave'),
                                          ('outstation','OutStation')],string='Attendence Status')
    state = fields.Selection(selection=[('draft','Draft'),('synch','Synch')],string='State')