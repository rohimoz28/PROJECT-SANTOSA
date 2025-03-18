# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class StoreProcedure(models.Model):
    _name = 'santosa_finance.store_procedure' # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Model Yang berisi Store Procedure' # Some note of table

    # Header
    name = fields.Char()
    tanggal_terakhir_dijalankan = fields.Datetime()
    populate_date = fields.Date()

    def panggil_store_procedure(self):
        for record in self:
            try:
                # Gunakan koneksi database Odoo
                self.env.cr.execute("CALL generate_transaction(%s)", (record.populate_date,))
                self.env.cr.commit()  # Commit perubahan jika diperlukan
                _logger.info('Stored procedure generate_transaction called successfully for record ID %s.', record.id)
                self.tanggal_terakhir_dijalankan = datetime.now()
            except Exception as e:
                _logger.error('Error calling stored procedure generate_transaction for record ID %s: %s', record.id, e)
                raise models.ValidationError('An error occurred for record ID {}: {}'.format(record.id, e))