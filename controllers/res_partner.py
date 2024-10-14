# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
from .sk_rest_api import RestApi

_logger = logging.getLogger(__name__)
rest_api_instance = RestApi()
check_method_instance = RestApi()
model = 'res.partner'


class ResPartnerRestApi(http.Controller):

    def prepare_value_res_partner(self, partner):
        value = {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
            'phone': partner.phone,
            'mobile': partner.mobile,
            'street': partner.street,
        }
        return value

    @http.route(['/list_contact'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_all_contact(self, **kw):
        http_method = request.httprequest.method
        api_key = request.httprequest.headers.get('api-key')
        # Checking authenticate by API-KEY and method
        checking_auth_api, is_auth = rest_api_instance.auth_api_key(api_key)
        if not is_auth:
            return request.make_response(json.dumps({'error': checking_auth_api}), status=401,
                                         headers=[('Content-Type', 'application/json')])
        checking_method, not_allow = check_method_instance.check_permission_method(http_method, model)
        if not_allow:
            return request.make_response(json.dumps({'error': checking_method}), status=403,
                                         headers=[('Content-Type', 'application/json')])

        # Execute method GET
        contacts = request.env['res.partner'].sudo().search([])
        result = []
        for contact in contacts:
            value = self.prepare_value_res_partner(contact)
            result.append(value)
        return request.make_response(json.dumps({'result': result}), headers=[('Content-Type', 'application/json')])

    @http.route(['/list_contact/<int:contact_id>'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_specific_contact(self, contact_id):
        http_method = request.httprequest.method
        api_key = request.httprequest.headers.get('api-key')
        # Checking authenticate by API-KEY and method
        checking_auth_api, is_auth = rest_api_instance.auth_api_key(api_key)
        if not is_auth:
            return request.make_response(json.dumps({'error': checking_auth_api}), status=401,
                                         headers=[('Content-Type', 'application/json')])
        checking_method, not_allow = check_method_instance.check_permission_method(http_method, model)
        if not_allow:
            return request.make_response(json.dumps({'error': checking_method}), status=403,
                                         headers=[('Content-Type', 'application/json')])

        contact = request.env['res.partner'].search([
            ('id', '=', contact_id)
        ])
        if contact:
            return request.make_response(json.dumps({'result': self.prepare_value_res_partner(contact)}),
                                         headers=[('Content-Type', 'application/json')])
        else:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: res.partner(%s,)' % contact_id}),
                status=404,
                headers=[('Content-Type', 'application/json')])

    @http.route(['/create_contact'], type='http',
                auth='public',
                methods=['POST'], csrf=False)
    def create_contact(self):
        http_method = request.httprequest.method
        raw_data = request.httprequest.data
        data_json = json.loads(raw_data)
        api_key = request.httprequest.headers.get('api-key')
        # Checking authenticate by API-KEY and method
        checking_auth_api, is_auth = rest_api_instance.auth_api_key(api_key)
        if not is_auth:
            return request.make_response(json.dumps({'error': checking_auth_api}), status=401,
                                         headers=[('Content-Type', 'application/json')])
        checking_method, not_allow = check_method_instance.check_permission_method(http_method, model)
        if not_allow:
            return request.make_response(json.dumps({'error': checking_method}), status=403,
                                         headers=[('Content-Type', 'application/json')])

        checking_contact = request.env['res.partner'].search([
            ('email', '=', data_json['email'])
        ])
        if checking_contact:
            return request.make_response(json.dumps({'error': 'Email already have, please choose other email'}),
                                         status=400,
                                         headers=[('Content-Type', 'application/json')])
        contact = request.env['res.partner'].sudo().create(data_json)
        return request.make_response(
            json.dumps({'result': 'Create successfully', 'data': self.prepare_value_res_partner(contact)}),
            headers=[('Content-Type', 'application/json')])

    @http.route(['/update_contact/<int:contact_id>'], type='http',
                auth='public',
                methods=['PUT'], csrf=False)
    def update_contact(self, contact_id):
        http_method = request.httprequest.method
        raw_data = request.httprequest.data
        data_json = json.loads(raw_data)
        # Checking authenticate by API-KEY and method
        api_key = request.httprequest.headers.get('api-key')
        checking_auth_api, is_auth = rest_api_instance.auth_api_key(api_key)
        if not is_auth:
            return request.make_response(json.dumps({'error': checking_auth_api}), status=401,
                                         headers=[('Content-Type', 'application/json')])
        checking_method, not_allow = check_method_instance.check_permission_method(http_method, model)
        if not_allow:
            return request.make_response(json.dumps({'error': checking_method}), status=403,
                                         headers=[('Content-Type', 'application/json')])

        contact = request.env['res.partner'].sudo().search([
            ('id', '=', contact_id)
        ])
        if not contact:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: res.partner(%s,)' % contact_id}), status=404,
                headers=[('Content-Type', 'application/json')])
        checking_contact = request.env['res.partner'].search([
            ('email', '=', data_json['email']),
            ('id', '!=', contact_id)
        ], limit=1)
        if checking_contact:
            return request.make_response(json.dumps({'error': 'Email already have, please choose other email'}),
                                         status=400,
                                         headers=[('Content-Type', 'application/json')])
        contact.write({
            'name': data_json['name'],
            'street': data_json['street'],
            'email': data_json['email'],
            'phone': data_json['phone'],
            'mobile': data_json['mobile']
        })
        return request.make_response(
            json.dumps({'result': 'Edit successfully', 'data': self.prepare_value_res_partner(contact)}),
            headers=[('Content-Type', 'application/json')])
