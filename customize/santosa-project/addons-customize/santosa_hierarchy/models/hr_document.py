from odoo import fields, models


class HrDocument(models.Model):
    """Creating hr document templates."""
    _name = 'hr.document'
    _description = 'HR Document Template '

    name = fields.Char(string='Document Name', required=True, copy=False,
                       help='You can give your Document name here.')
    note = fields.Text(string='Note', copy=False, help="Note of the document.")
    attach_ids = fields.Many2many('ir.attachment',
                                  'attach_rel', 'doc_id',
                                  'attach_id3', string="Attachment",
                                  help='You can attach the copy of your'
                                       ' document.', copy=False)