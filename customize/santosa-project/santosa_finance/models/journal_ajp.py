from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import pytz
from babel.dates import format_datetime


class JournalAJPType(models.Model):
    _name = 'journal.ajp.type'
    _description = 'Journal AJP Type'

    name = fields.Char('Name', index=True,required=True)
    code = fields.Char('Code',size=6, index=True,required=True)
    active = fields.Boolean(default=True)
    descr = fields.Char('Description')

class JournalAJP(models.Model):
    _name = 'journal.ajp'
    _description = 'Journal AJP'

    name = fields.Char('Name', index=True,required=True)
    code = fields.Char('Code',size=6, index=True,required=True)
    type = fields.Many2one('journal.ajp.type','Type', index=True,required=True)
    active = fields.Boolean(default=True)
    descr = fields.Char('Description')