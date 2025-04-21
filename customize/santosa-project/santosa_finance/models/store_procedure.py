# -*- coding: utf-8 -*-

from odoo import models, fields, api # Mandatory
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class StoreProcedure(models.Model):
    _name = 'santosa_finance.store_procedure' # name_of_module.name_of_class
    _rec_name = 'name'
    _description = 'Model Yang berisi Store Procedure' # Some note of table
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    # Header
    name = fields.Char()
    tanggal_terakhir_dijalankan = fields.Datetime(
        default=lambda self:datetime.now()
    )
    populate_date = fields.Date(
        default=lambda self:date.today())
    order_lines_ids = fields.One2many('santosa_finance.missing_coa','order_id')

    def panggil_store_procedure(self):
        for record in self:
            try:
                # Gunakan koneksi database Odoo
                self.env.cr.execute("CALL generate_transaction(%s)", (record.populate_date,))
                self.env.cr.commit()  # Commit perubahan jika diperlukan
                _logger.info('Stored procedure generate_transaction called successfully for record ID %s.', record.id)
                self.tanggal_terakhir_dijalankan = datetime.now()
                self.message_post(body=("Procedure run at %s with pupulate date %s")%(datetime.now(),self.populate_date))
            except Exception as e:
                _logger.error('Error calling stored procedure generate_transaction for record ID %s: %s', record.id, e)
                raise models.ValidationError('An error occurred for record ID {}: {}'.format(record.id, e))

    def generate_line(self):
        for line in self:
            query = """
                truncate table santosa_finance_missing_coa;
                INSERT INTO santosa_finance_missing_coa (
                    populate_date,
                    order_id,
                    sales_point,
                    item_group_name,
                    item_group_key,
                    coa_patient_key,
                    create_uid,
                    write_uid
                )
                SELECT DISTINCT
                    PopulatedTime"::date AS populate_date,
                    %s AS order_id,
                    d."SalesPoint" AS sales_point,
                    d."ItemGroupName" AS item_group_name,
                    d."ItemGroupKey" AS item_group_key,
                    d."COA_patient_Key" AS coa_patient_key,1,1
                FROM
                    santosa_finance_stg_invoice_lines d
                LEFT JOIN
                    santosa_finance_akun_kategori f
                    ON substring(d."SalesPoint" from 2 for 1)::int = f."SalesPoint"
                    AND upper(d."ItemGroupName") = upper(f.name)
                WHERE
                    f."name" IS NULL 
                    AND "PopulatedTime"::date = '%s'
                    AND d."ItemGroupKey" <> '11';
            """
            try:
                self.env.cr.execute((query)%(line.id,line.populate_date))
            except Exception as e:
                _logger.error(f"Error executing query: {e}")
                raise UserError(f"Error executing query: {e}")

class MissingCoa(models.Model):
    _name = 'santosa_finance.missing_coa'
    _description = 'COA Doesnt Register'  # Some note of table

    order_id = fields.Many2one(string='Generate SP', comodel_name='santosa_finance.store_procedure')
    populate_date = fields.Date('PopulatedTime')
    sales_point = fields.Char('SalesPoint', help="Point of sale where the transaction was recorded.")
    item_group_name = fields.Char('ItemGroupName', help="Name of the item group.")
    item_group_key = fields.Char('ItemGroupKey', help="Unique identifier for the item group.")
    coa_patient_key = fields.Char('COA_patient_Key', help="Unique identifier for the patient's COA.")