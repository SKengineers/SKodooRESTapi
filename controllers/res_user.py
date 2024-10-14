# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
from .sk_rest_api import RestApi

_logger = logging.getLogger(__name__)
rest_api_instance = RestApi()
check_method_instance = RestApi()
model = 'res.users'
user_lang = 'en_US'


class ResUserRestApi(http.Controller):

    def prepare_value_res_user(self, user, api_key):
        value = {
            'id': user.id,
            'name': user.name,
            'login': user.login,
        }
        if user.api_key == api_key:
            value.update({
                'api_key': api_key
            })
        return value

    @http.route(['/list_user'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_all_user(self, **kw):
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
        res_user = request.env['res.users'].sudo().search([])
        result = []
        for user in res_user:
            value = self.prepare_value_res_user(user, api_key)
            result.append(value)
        return request.make_response(json.dumps({'result': result}), headers=[('Content-Type', 'application/json')])

    @http.route(['/list_user/<int:user_id>'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_specific_user(self, user_id):
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

        user = request.env['res.users'].search([
            ('id', '=', user_id)
        ])
        if user:
            return request.make_response(json.dumps({'result': self.prepare_value_res_user(user, api_key)}),
                                         headers=[('Content-Type', 'application/json')])
        else:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: res.users(%s,)' % user_id}),
                status=404,
                headers=[('Content-Type', 'application/json')])

    @http.route(['/create_user'], type='http',
                auth='public',
                methods=['POST'], csrf=False)
    def create_res_user(self):
        http_method = request.httprequest.method
        raw_data = request.httprequest.data
        data_json = json.loads(raw_data)
        user = request.env['res.users']
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

        checking_user = request.env['res.users'].search([
            ('login', '=', data_json['login'])
        ])
        if checking_user:
            return request.make_response(json.dumps({'error': 'Login already have, please choose other login'}),
                                         status=400,
                                         headers=[('Content-Type', 'application/json')])
        request.env['res.users'].sudo().signup(data_json)
        new_user = user.sudo().search([("login", "=", data_json['login'])], limit=1)

        new_user.write({'lang': user_lang})

        new_user.partner_id.write({
            'phone': data_json['phone'],
            'mobile': data_json['mobile'],
            'street': data_json['street'],
            'name': data_json['name'],
        })
        return request.make_response(
            json.dumps({'result': 'Create successfully', 'data': self.prepare_value_res_user(new_user, api_key)}),
            headers=[('Content-Type', 'application/json')])

    @http.route(['/update_user/<int:user_id>'], type='http',
                auth='public',
                methods=['PUT'], csrf=False)
    def update_user(self, user_id):
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

        user = request.env['res.users'].sudo().search([
            ('id', '=', user_id)
        ])
        if not user:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: res.users(%s,)' % user_id}), status=404,
                headers=[('Content-Type', 'application/json')])
        if user.api_key != api_key:
            return request.make_response(json.dumps(
                {'result': 'You cannot change data for the other user'}), status=403,
                headers=[('Content-Type', 'application/json')])
        user.write({
            'password': data_json['password'],
            'name': data_json['name']
        })
        user.partner_id.write({
            'name': data_json['name'],
            'phone': data_json['phone'],
            'street': data_json['street'],
            'mobile': data_json['mobile']
        })
        return request.make_response(
            json.dumps({'result': 'Edit successfully', 'data': self.prepare_value_res_user(user, api_key)}),
            headers=[('Content-Type', 'application/json')])
