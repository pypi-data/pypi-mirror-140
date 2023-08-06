# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.asgi import _scope_to_environ


def asgi_to_environ(scope, receive):
    """
    According to this doc here in the HTTP Connection Scope
    section: https://asgi.readthedocs.io/en/latest/specs/www.html#http
    it seems like most of the items found in scope can be directly converted into environ

    In a generic case we will have to await the receive callable and verify the message type is
    http.request in order to get the request body
    """
    # body = b""
    # more_body = True
    #
    # while more_body:
    #     try:
    #         data = await receive()
    #
    #         if data.get("type") == "http.request":
    #             body += data.get("body")
    #         else:
    #             """
    #             We are consuming messages here so we need a way to
    #             re add the message so other MWs/app code can still await it.
    #
    #             We will most likely have to do something similar to _get_body_non_destructive
    #             """
    #             break
    #
    #         more_body = data.get("more_body", False)
    #     except Exception:
    #         break
    #
    environ = _scope_to_environ(scope, b"")

    return environ
