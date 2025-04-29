# -*- coding: utf-8 -*-
# from odoo import http


# class SantosaHrTraining(http.Controller):
#     @http.route('/santosa_hr_training/santosa_hr_training', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/santosa_hr_training/santosa_hr_training/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('santosa_hr_training.listing', {
#             'root': '/santosa_hr_training/santosa_hr_training',
#             'objects': http.request.env['santosa_hr_training.santosa_hr_training'].search([]),
#         })

#     @http.route('/santosa_hr_training/santosa_hr_training/objects/<model("santosa_hr_training.santosa_hr_training"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('santosa_hr_training.object', {
#             'object': obj
#         })

