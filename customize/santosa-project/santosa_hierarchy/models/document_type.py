from odoo import fields, models


class DocumentType(models.Model):
    """This model is used to categorize and manage various document
     types in the system."""
    _name = 'document.type'
    _description = 'Document Type'

    name = fields.Char(string="Name", required=True,
                       help="Name of the document type")