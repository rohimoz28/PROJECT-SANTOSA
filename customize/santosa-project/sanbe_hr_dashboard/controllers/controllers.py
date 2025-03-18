# -*- coding: utf-8 -*-
# from odoo import http


# class Infomedia(http.Controller):
#     @http.route('/infomedia/infomedia', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/infomedia/infomedia/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('infomedia.listing', {
#             'root': '/infomedia/infomedia',
#             'objects': http.request.env['infomedia.infomedia'].search([]),
#         })

#     @http.route('/infomedia/infomedia/objects/<model("infomedia.infomedia"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('infomedia.object', {
#             'object': obj
#         })

