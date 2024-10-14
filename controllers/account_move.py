# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
from .sk_rest_api import RestApi

_logger = logging.getLogger(__name__)
rest_api_instance = RestApi()
check_method_instance = RestApi()
model = 'account.move'


class ProductRestApi(http.Controller):

    def prepare_value_invoice(self, invoice):
        source_orders = invoice.line_ids.sale_line_ids.order_id
        value = {
            'id': invoice.id,
            'name': invoice.name,
            'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            'state': invoice.state,
            'sale_order':
                {
                    'id': source_orders.id,
                    'name': source_orders.name
                },
            'payment_reference': invoice.payment_reference,
            'amount_untaxed': invoice.amount_untaxed,
            'amount_tax': invoice.amount_tax,
            'amount_total': invoice.amount_total,
            'amount_residual': invoice.amount_residual,
            'invoice_line': [{'product_id': line.product_id.id,
                              'name': line.name,
                              'quantity': line.quantity,
                              'price_unit': line.price_unit,
                              'price_subtotal': line.price_subtotal} for line in invoice.invoice_line_ids]
        }
        return value

    @http.route(['/list_invoice'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_all_invoice(self, **kw):
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
        invoice = request.env['account.move'].sudo().search([
            ('move_type', '=', 'out_invoice')
        ])
        result = []
        for inv in invoice:
            value = self.prepare_value_invoice(inv)
            result.append(value)
        print(result)
        return request.make_response(json.dumps({'result': result}), headers=[('Content-Type', 'application/json')])

    @http.route(['/list_invoice/<int:invoice_id>'], type='http',
                auth='public',
                methods=['GET'], csrf=False)
    def search_specific_invoice(self, invoice_id):
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

        invoice = request.env['account.move'].sudo().search([
            ('id', '=', invoice_id)
        ])
        if invoice:
            return request.make_response(json.dumps({'result': self.prepare_value_invoice(invoice)}),
                                         headers=[('Content-Type', 'application/json')])
        else:
            return request.make_response(json.dumps(
                {'result': 'Record does not exit or has been delete. Record: account.move(%s,)' % invoice_id}),
                status=404,
                headers=[('Content-Type', 'application/json')])
