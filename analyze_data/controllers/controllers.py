# -*- coding: utf-8 -*-
from odoo import http

# class AnalyzeData(http.Controller):
#     @http.route('/analyze_data/analyze_data/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/analyze_data/analyze_data/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('analyze_data.listing', {
#             'root': '/analyze_data/analyze_data',
#             'objects': http.request.env['analyze_data.analyze_data'].search([]),
#         })

#     @http.route('/analyze_data/analyze_data/objects/<model("analyze_data.analyze_data"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('analyze_data.object', {
#             'object': obj
#         })