# -*- coding: utf-8 -*-
from odoo import http

# class AdditionalChanges(http.Controller):
#     @http.route('/additional_changes/additional_changes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/additional_changes/additional_changes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('additional_changes.listing', {
#             'root': '/additional_changes/additional_changes',
#             'objects': http.request.env['additional_changes.additional_changes'].search([]),
#         })

#     @http.route('/additional_changes/additional_changes/objects/<model("additional_changes.additional_changes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('additional_changes.object', {
#             'object': obj
#         })