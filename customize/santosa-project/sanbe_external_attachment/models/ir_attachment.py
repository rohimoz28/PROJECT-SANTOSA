# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
import paramiko
import base64
import binascii
import contextlib
import hashlib
import io
import itertools
import logging
import mimetypes
import os
import psycopg2
import re
import uuid

from collections import defaultdict
from PIL import Image

from odoo import api, fields, models, SUPERUSER_ID, tools, _
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.tools import config, human_size, ImageProcess, str2bool, consteq
from odoo.tools.mimetypes import guess_mimetype
from odoo.osv import expression
from io import BytesIO
_logger = logging.getLogger(__name__)

koneksi = False
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'



    def buka_sftp(self):
        koneksi = paramiko.SSHClient()
        koneksi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        koneksi.connect(hostname='192.168.16.133', username='albert', password='@lbert@2023', banner_timeout=100)
        return koneksi.open_sftp()

    def sftp_dir_exists(self,sftp, path):
        try:
            myfile1 = str(path).replace('\\', '/')
            myfile2 = str(myfile1).replace('\\', '/')
            sftp.stat(myfile2)
            return True
        except FileNotFoundError:
            return False

    def sftp_make_dir(self,sftp,remote_path):
        rpath = os.path.dirname(remote_path)
        mypath = rpath.replace('\\', '/')
        try:

            sftp.chdir(mypath)  # Test if remote_path exists
        except IOError:
            sftp.mkdir(mypath)  # Create remote_path
            sftp.chdir(mypath)

    def adafile(self,sftp,filename):
        rpath = os.path.dirname(filename)
        mypath = rpath.replace('\\','/')
        myfile = str(filename).replace('\\','/')
        sftp.chdir(mypath)
        try:
            with sftp.open(myfile,'rb') as remote_file:
                datanya = None
                for line in remote_file:
                    datanya=line
                sftp.close()
                return datanya
        except Exception as err:
          print ("SFTP failed due to [" + str(err) + "]")

    def bukafile(self,sftp,filename,op):
        rpath = os.path.dirname(filename)
        mypath = rpath.replace('\\','/')
        myfile = str(filename).replace('\\','/')
        sftp.chdir(mypath)
        try:
            remote_file = sftp.open(myfile,op)
            sftp.close()
        except Exception as err:
          print ("SFTP failed due to [" + str(err) + "]")

    @api.model
    def _full_path(self, path):
        # sanitize path
        path = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join('/opt/OdooSanbe/filestore/filestore/SANBE_HRMS', path)

    @api.model
    def _get_path(self, bin_data, sha):
        fname = sha[:3] + '/' + sha
        full_path = self._full_path(fname)
        sftp = self.buka_sftp()
        if self.sftp_dir_exists(sftp,full_path):
            return fname, full_path        # keep existing path
        fname = sha[:2] + '/' + sha
        full_path = self._full_path(fname)
        dirname = os.path.dirname(full_path)
        if not self.sftp_dir_exists(sftp,dirname):
            self.sftp_make_dir(sftp,dirname)
        if self.sftp_dir_exists(sftp,full_path) and not self._same_content(sftp,bin_data, full_path):
            raise UserError(_("The attachment collides with an existing file."))
        return fname, full_path

    @api.model
    def _file_read(self, fname):
        sftp = self.buka_sftp()
        assert isinstance(self, IrAttachment)
        full_path = self._full_path(fname)
        try:
            return self.adafile(sftp,full_path)
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return b''

    @api.model
    def _file_write(self, bin_value, checksum):
        sftp = self.buka_sftp()
        assert isinstance(self, IrAttachment)
        fname, full_path = self._get_path(bin_value, checksum)
        if  self.sftp_dir_exists(sftp,full_path):
            try:
                myfile = str(full_path).replace('\\', '/')
                with sftp.open(myfile, "wb") as f:
                    f.write(bin_value)
                    f.close()
                sftp.close()
                self._mark_for_gc(fname)
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return fname

    @api.model
    def _file_delete(self, fname):
        self._mark_for_gc(fname)

    def _mark_for_gc(self, fname):
        assert isinstance(self, IrAttachment)
        sftp = self.buka_sftp()
        fname = re.sub('[.]', '', fname).strip('/\\')
        # we use a spooldir: add an empty file in the subdirectory 'checklist'
        full_path = os.path.join(self._full_path('checklist'), fname)
        if self.sftp_dir_exists(sftp,full_path):
            dirname = os.path.dirname(full_path)
            if not self.sftp_dir_exists(sftp,dirname):
                with contextlib.suppress(OSError):
                    self.sftp_make_dir(self,dirname)
            self.bukafile(sftp,full_path, 'ab')


    def _gc_file_store_unsafe(self):
        checklist = {}
        for dirpath, _, filenames in os.walk(self._full_path('checklist')):
            dirname = os.path.basename(dirpath)
            for filename in filenames:
                fname = "%s/%s" % (dirname, filename)
                checklist[fname] = os.path.join(dirpath, filename)
        removed = 0
        for names in self.env.cr.split_for_in_conditions(checklist):
            # determine which files to keep among the checklist
            self.env.cr.execute("SELECT store_fname FROM ir_attachment WHERE store_fname IN %s", [names])
            whitelist = set(row[0] for row in self.env.cr.fetchall())

            # remove garbage files, and clean up checklist
            for fname in names:
                filepath = checklist[fname]
                if fname not in whitelist:
                    try:
                        os.unlink(self._full_path(fname))
                        _logger.debug("_file_gc unlinked %s", self._full_path(fname))
                        removed += 1
                    except (OSError, IOError):
                        _logger.info("_file_gc could not unlink %s", self._full_path(fname), exc_info=True)
                with contextlib.suppress(OSError):
                    os.unlink(filepath)

        _logger.info("filestore gc %d checked, %d removed", len(checklist), removed)

    @api.model
    def _same_content(self, sftp, bin_data, filepath):
        rpath = os.path.dirname(filepath)
        mypath = rpath.replace('\\','/')
        myfile = str(filepath).replace('\\','/')
        sftp.chdir(mypath)
        BLOCK_SIZE = 1024
        try:
            with sftp.open(myfile,'rb') as remote_file:
                datanya = None
                for line in remote_file:
                    datanya=line
                if bin_data == datanya:
                    return False
                else:
                    return True
        except Exception as err:
          print ("SFTP failed due to [" + str(err) + "]")
          return False
