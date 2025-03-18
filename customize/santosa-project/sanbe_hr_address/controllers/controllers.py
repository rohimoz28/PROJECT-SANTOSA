# -*- coding: utf-8 -*-
# from odoo import http


# class TribhaktiStock(http.Controller):
#     @http.route('/tribhakti_stock/tribhakti_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tribhakti_stock/tribhakti_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tribhakti_stock.listing', {
#             'root': '/tribhakti_stock/tribhakti_stock',
#             'objects': http.request.env['tribhakti_stock.tribhakti_stock'].search([]),
#         })

#     @http.route('/tribhakti_stock/tribhakti_stock/objects/<model("tribhakti_stock.tribhakti_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tribhakti_stock.object', {
#             'object': obj
#         })
