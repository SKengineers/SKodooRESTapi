# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
from .sk_rest_api import RestApi

_logger = logging.getLogger(__name__)
rest_api_instance = RestApi()
check_method_instance = RestApi()
model = 'product.product'


class ProductRestApi(http.Controller):

    def prepare_value_product(self, product):
        select = product.fields_get(allfields=['detailed_type'])['detailed_type']['selection']
        selection_dict = dict(select)
        value = {
            'id': product.id,
            'name': product.product_tmpl_id.display_name,
            'sale_price': product.lst_price,
            'type': selection_dict.get(product.detailed_type),
            'internal_reference': product.default_code,
            'barcode': product.barcode
        }
        return value

    @http.route(['/list_product'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_all_product(self, **kw):
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
        products = request.env['product.product'].sudo().search([])
        result = []
        for product in products:
            value = self.prepare_value_product(product)
            result.append(value)
        return request.make_response(json.dumps({'result': result}), headers=[('Content-Type', 'application/json')])

    @http.route(['/list_product/<int:product_id>'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_specific_product(self, product_id):
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

        product = request.env['product.product'].sudo().search([
            ('id', '=', product_id)
        ])
        if product:
            return request.make_response(json.dumps({'result': self.prepare_value_product(product)}),
                                         headers=[('Content-Type', 'application/json')])
        else:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: product.product(%s,)' % product_id}),
                status=404,
                headers=[('Content-Type', 'application/json')])
