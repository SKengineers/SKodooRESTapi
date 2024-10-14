# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)

HTTP_METHOD_GET = 'GET'
HTTP_METHOD_POST = 'POST'
HTTP_METHOD_PUT = 'PUT'
HTTP_METHOD_DELETE = 'DELETE'


class RestApi(http.Controller):
    """This is a controller which is used to generate responses based on the
    api requests"""

    def has_permission(self, option, allowed_method):
        if option and not allowed_method:
            return True
        return False

    def check_permission_method(self, method, model):
        # Checking method for API
        option = request.env['connection.api'].sudo().search(
            [('model_id', '=', model)], limit=1)

        if method == HTTP_METHOD_GET and self.has_permission(option, option.is_get):
            return "GET Method Not Allowed For API", True
        if method == HTTP_METHOD_POST and self.has_permission(option, option.is_post):
            return "POST Method Not Allowed For API", True
        if method == HTTP_METHOD_PUT and self.has_permission(option, option.is_put):
            return "PUT Method Not Allowed For API", True
        # if method == HTTP_METHOD_DELETE and self.has_permission(option, option.is_delete):
        #     return "DELETE Method Not Allowed For API", True

        return "Method Allowed", False

    def auth_api_key(self, api_key):
        """This function is used to authenticate the api-key when sending a
        request"""
        user_id = request.env['res.users'].sudo().search([('api_key', '=', api_key)])
        if api_key is not None and user_id:
             return 'API Key Provided', True
        elif not user_id or api_key is None:
            return 'Invalid API Key', False
        else:
            return "API Key Provided", True

    @http.route(['/odoo_connect'], type="http", auth="none", csrf=False,
                methods=['GET'])
    def odoo_connect(self, **kw):
        """This is the controller which initializes the api transaction by
        generating the api-key for specific user and database"""

        username = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        db = request.httprequest.headers.get('db')
        try:
            request.session.update(http.get_default_session(), db=db)
            auth = request.session.authenticate(request.session.db, username,
                                                password)
            user = request.env['res.users'].browse(auth)
            api_key = request.env.user.generate_api(username)
            datas = json.dumps({"Status": "auth successful",
                                "User": user.name,
                                "api-key": api_key})
            return request.make_response(data=datas)
        except:
            return ("<html><body><h2>wrong login credentials"
                    "</h2></body></html>")
