# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
from .sk_rest_api import RestApi
_logger = logging.getLogger(__name__)
rest_api_instance = RestApi()
check_method_instance = RestApi()
model = 'purchase.order'


class PurchaseOrderRestAPI(http.Controller):

    def prepare_value_purchase_order(self, purchase_order):
        return {
                'id': purchase_order.id,
                'name': purchase_order.name,
                'create_date': purchase_order.create_date.strftime('%Y-%m-%d %H:%M:%S') if purchase_order.create_date else None,
                'modify_date': purchase_order.write_date.strftime('%Y-%m-%d %H:%M:%S') if purchase_order.write_date else None,
                'date_order': purchase_order.date_order.strftime('%Y-%m-%d %H:%M:%S') if purchase_order.date_order else None,
                'partner': {
                    'id': purchase_order.partner_id.id,
                    'name': purchase_order.partner_id.name
                },
                'state': purchase_order.state,
                'amount_untaxed': purchase_order.amount_untaxed,
                'amount_tax': purchase_order.amount_tax,
                'amount_total': purchase_order.amount_total,
                'notes': purchase_order.notes,
                'oder_line': [{'product_id': line.product_id.id,
                               'name': line.name,
                               'product_qty': line.product_uom_qty,
                               'price_unit': line.price_unit,
                               'price_subtotal': line.price_subtotal} for line in purchase_order.order_line]
            }

    @http.route(['/list_purchase_order'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_all_purchase_order(self, **kw):
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
        purchase_order = request.env['purchase.order'].sudo().search([])
        result = []
        for purchase in purchase_order:
            value = self.prepare_value_purchase_order(purchase)
            result.append(value)
        return request.make_response(json.dumps({'result': result}), headers=[('Content-Type', 'application/json')])

    @http.route(['/list_purchase_order/<int:purchase_order_id>'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_specific_purchase_order(self, purchase_order_id):
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

        purchase_order = request.env['purchase.order'].sudo().search([
            ('id', '=', purchase_order_id)
        ])
        if purchase_order:
            return request.make_response(json.dumps({'result': self.prepare_value_purchase_order(purchase_order)}), headers=[('Content-Type', 'application/json')])
        else:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: sale.order(%s,)' % purchase_order_id}),
                                         status=404,
                                         headers=[('Content-Type', 'application/json')])

    @http.route(['/create_purchase_order'], type='http',
                auth='public',
                methods=['POST'], csrf=False)
    def create_purchase_order(self):
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

        if 'partner_id' not in data_json:
            return request.make_response(json.dumps({'error': 'One of the given parameters is not valid'}), status=400,
                                         headers=[('Content-Type', 'application/json')])

        partner = request.env['res.partner'].search([
            ('id', '=', data_json['partner_id'])
        ])
        if not partner:
            return request.make_response(json.dumps({'error': 'Cannot found partner you request'}), status=404,
                                         headers=[('Content-Type', 'application/json')])
        purchase_order = request.env['purchase.order'].create({
            'partner_id': partner.id
        })
        return request.make_response(json.dumps({'result': 'Create successfully', 'data': self.prepare_value_purchase_order(purchase_order)}),
                                     headers=[('Content-Type', 'application/json')])

    @http.route(['/create_purchase_order_with_line'], type='http',
                auth='public',
                methods=['POST'], csrf=False)
    def create_purchase_order_with_line(self):
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

        if 'partner_id' not in data_json or 'order_line' not in data_json:
            return request.make_response(json.dumps({'error': 'One of the given parameters is not valid'}), status=400,
                                         headers=[('Content-Type', 'application/json')])
        partner = request.env['res.partner'].search([
            ('id', '=', data_json['partner_id'])
        ])
        if not partner:
            return request.make_response(json.dumps({'error': 'Cannot found partner you request'}), status=404,
                                         headers=[('Content-Type', 'application/json')])
        purchase_order = request.env['purchase.order'].create({
            'partner_id': partner.id
        })
        for val in data_json['order_line']:
            val['order_id'] = purchase_order.id
            product = request.env['product.product'].search([
                ('id', '=', val['product_id'])
            ])
            if not product:
                return request.make_response(json.dumps({'error': 'Cannot found product you request'}), status=404,
                                             headers=[('Content-Type', 'application/json')])
            if product and not product.purchase_ok:
                return request.make_response(json.dumps({'error': 'Product %s can not be purchase' % product.display_name}), status=404,
                                             headers=[('Content-Type', 'application/json')])
            request.env['purchase.order.line'].create(val)
        return request.make_response(json.dumps({'result': 'Create successfully', 'data': self.prepare_value_purchase_order(purchase_order)}),
                                     headers=[('Content-Type', 'application/json')])

    @http.route(['/update_purchase_order/<int:purchase_order_id>'], type='http',
                auth='public',
                methods=['PUT'], csrf=False)
    def update_purchase_order(self, purchase_order_id):
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

        purchase_order = request.env['purchase.order'].sudo().search([
            ('id', '=', purchase_order_id)
        ])
        if not purchase_order:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: purchase.order(%s,)' % purchase_order_id}),
                                         status=404,
                                         headers=[('Content-Type', 'application/json')])

        if purchase_order.state == 'sale' and (sum(purchase_order.mapped('order_line.qty_invoiced')) > 0 or sum(
                purchase_order.mapped('order_line.qty_received')) > 0):
            return request.make_response(json.dumps({'result': 'Edit Fail',
                                                     'reason': 'Purchase Order have been created Invoice and Delivery, cannot change data'}),
                                         status=403,
                                         headers=[('Content-Type', 'application/json')])
        order_line = data_json['order_line']
        if order_line:
            purchase_order.order_line.unlink()
            for line in order_line:
                purchase_order.write({
                    'order_line': [(0, 0, {
                        'product_id': line['product_id'],
                        'product_qty': line['product_qty'],
                        'price_unit': line['price_unit']
                    })]
                })
            del data_json['order_line']
        if data_json:
            if 'state' in data_json and data_json['state'] == 'sale':
                purchase_order.button_confirm()
            purchase_order.write(data_json)
        return request.make_response(json.dumps({'result': 'Edit successfully', 'data': self.prepare_value_purchase_order(purchase_order)}),
                                     headers=[('Content-Type', 'application/json')])

    @http.route(['/delete_purchase_order/<int:purchase_order_id>'], type='http',
                auth='public',
                methods=['DELETE'], csrf=False)
    def delete_purchase_order(self, purchase_order_id):
        http_method = request.httprequest.method
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

        purchase_order = request.env['purchase.order'].sudo().search([
            ('id', '=', purchase_order_id)
        ])
        if not purchase_order:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: purchase.order(%s,)' % purchase_order_id}),
                status=404,
                headers=[('Content-Type', 'application/json')])
        if purchase_order.state not in ['draft', 'cancel']:
            return request.make_response(json.dumps(
                {'result': 'Purchase order cannot delete. Record: purchase.order(%s,)' % purchase_order_id}), status=403,
                headers=[('Content-Type', 'application/json')])
        purchase_order.order_line.unlink()
        purchase_order.button_cancel()
        purchase_order.unlink()

        return request.make_response(
            json.dumps({'result': 'Delete successfully', 'data': 'Purchase Order ID: %s' % purchase_order_id}),
            headers=[('Content-Type', 'application/json')])