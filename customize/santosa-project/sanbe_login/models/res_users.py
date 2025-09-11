# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request, DEFAULT_LANG
import logging
from random import choice
from string import digits
try:
  import qrcode
except ImportError:
  qrcode = None
try:
  import base64
except ImportError:
  base64 = None
from io import BytesIO
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    res_users_image_ids = fields.One2many('res.users.image', 'res_user_id', string='Face recognition user images', copy=True,auto_join=True)
    face_emotion = fields.Selection([
        ('neutral', 'neutral'),
        ('happy', 'happy'),
        ('sad', 'sad'),
        ('angry', 'angry'),
        ('fearful', 'fearful'),
        ('disgusted', 'disgusted'),
        ('surprised', 'surprised'),
        ('any', 'any')
    ], string='Emotion', required=True, default='any', help='The emotion that must be performed for access')
    face_gender = fields.Selection([
        ('male', 'male'),
        ('female', 'female'),
        ('any', 'any')
    ], string='Gender', required=True, default='any', help='Gender to be Accessed')
    face_age = fields.Selection([
        ('20', '0-20'),
        ('30', '20-30'),
        ('40', '30-40'),
        ('50', '40-50'),
        ('60', '50-60'),
        ('70', '60-any'),
        ('any', 'any')
    ], string='Age', required=True, default='any', help='Age for accessd')
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user", copy=False)
    qr_code = fields.Binary("QR Code", compute='generate_qr_code')

    @api.depends('barcode')
    def generate_qr_code(self):
        for allrec in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                qr.add_data(allrec.barcode)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                allrec.update({'qr_code': qr_image})
    def generate_random_barcode(self):
        for employee in self:
            employee.barcode = '041'+"".join(choice(digits) for i in range(9))
    def _check_credentials(self, password, env):
        """ Override this method to plug additional authentication methods"""
        assert password
        self.env.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
            [self.env.user.id]
        )
        [hashed] = self.env.cr.fetchone()
        valid, replacement = self._crypt_context()\
            .verify_and_update(password, hashed)
        if replacement is not None:
            self._set_encrypted_password(self.env.user.id, replacement)
        if not valid:
            raise AccessDenied()

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth(user=login):
                    user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password, user_agent_env)
                    tz = request.httprequest.cookies.get('tz') if request else None
                    # if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                    #     # first login or missing tz -> set tz to browser tz
                    #     user.tz = tz
                    user._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise

        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

        return user.id
class UserImage(models.Model):
    _name = 'res.users.image'
    _description = 'User Image'
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer(string='Sequence data', default=10, index=True)
    image = fields.Image(string='Image Recognizer', required=True)
    image_detection = fields.Image(string='Image Detection')
    res_user_id = fields.Many2one('res.users', string='User ID', index=True, ondelete='cascade')

