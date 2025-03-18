# -*- coding: utf-8 -*-

from odoo import http, tools
from odoo.http import request
import json
from  passlib.context import CryptContext
import base64
import hashlib
import secrets

ALGORITHM = "pbkdf2_sha256"

class FaceLoginWeb(http.Controller):

    @http.route('/init_login',  type='json', auth='none', cors='*', csrf=False)
    def read_user_data(self, **kw):
        face_recognition_enable = True
        face_recognition_store = False
        user_name = []
        user_id = request.env['res.users'].sudo().search([('login', '=', 'admin')])
        alluser = request.env['res.users'].sudo().search([])
        for allusers in alluser:
            user_name.append(allusers.name)
        alluser_data = request.env['res.users.image'].sudo().search([('image', '!=', False)])
        images_ids = alluser_data.mapped('image')
        labels_ids = alluser_data.mapped('res_user_id.login')
        return {
            'face_recognition_enable': True if face_recognition_enable else False,
            'face_recognition_store': True if face_recognition_store else False,
            'images_ids': images_ids,
            'labels_ids': labels_ids,
            'face_emotion': user_id.face_emotion,
            'face_gender': user_id.face_gender,
            'face_age': user_id.face_age,
            'user_name': user_name
        }

    @http.route('/get_login_info',  type='http', auth='none', cors='*', csrf=False)
    def read_user_login_info(self, auth_token):
        # request.env.cr.execute(
        #     "SELECT password  FROM res_users WHERE login=%s",
        #     [auth_token]
        # )
        request.env.cr.execute(
            "SELECT password FROM res_users WHERE login=%s",
            [auth_token]
        )

        # pwd =  request.env['res.users']._crypt_context().identify(hashed)
        passwordnya = request.env.cr.fetchone()
        setpw = CryptContext(schemes=['pbkdf2_sha512'])
        passwd = str(str(str(passwordnya).replace('(','')).replace(',)','')).replace("'",'')
        # print('password ', ssha512.decode('utf-8'))
        # myuser = request.env['res.users'].sudo().search([('login','=',auth_token)])
        return  passwd


    @http.route('/get_login_idcard',  type='http', auth='none', cors='*', csrf=False)
    def login_with_idcards(self,idcard):
        myuser = request.env['res.users'].sudo().search([('barcode','=',idcard)])
        if myuser:
            return 'success'
        else:
            return 'failed'
