# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from quart import Response

from contrast.agent.middlewares.asgi_middleware import AsgiMiddleware
from contrast.utils.exceptions.security_exception import SecurityException


class QuartMiddleware(AsgiMiddleware):
    def generate_security_exception_response(self):
        return Response(
            response=self.OVERRIDE_MESSAGE,
            status=SecurityException.STATUS_CODE,
            content_type="text/html",
        )
