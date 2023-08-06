# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast

from .sources import asgi_to_environ
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.request_context import RequestContext
from contrast.agent.asgi import track_scope_sources
from contrast.utils.decorators import log_time_cm
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.utils import Profiler
from contrast.extern import structlog as logging


logger = logging.getLogger("contrast")


class AsgiMiddleware(BaseMiddleware):
    def __init__(self, app):
        self.app = app
        self.asgi_app = app.asgi_app
        self.app_name = app.name
        super().__init__()

    async def call_with_agent(self, context, scope, receive, send):
        path = scope.get("path")
        self.log_start_request_analysis(path)

        track_scope_sources(context, scope)

        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                # self.asgi_app doesn't return anything will need to instrument send
                await self.asgi_app(scope, receive, send)

            # self.postfilter(context)
            # self.check_for_blocked(context)
            return
        except ContrastServiceException as e:
            logger.warning(e)
            return await self.call_without_agent_async(scope, receive, send, path)
        except Exception as e:
            response = self.handle_exception(e)
            return response
        finally:
            self.handle_ensure(context, context.request)
            self.log_end_request_analysis(context.request.path)
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    async def __call__(self, scope, receive, send):
        path = scope.get("path")

        with Profiler(path):
            if self.is_agent_enabled():
                if self.settings.ignore_request(path):
                    return await self.call_without_agent_async(
                        scope, receive, send, path
                    )

                environ = asgi_to_environ(scope, receive)

                context = RequestContext(environ)
                with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                    return await self.call_with_agent(context, scope, receive, send)

        return await self.call_without_agent_async(scope, receive, send, path)

    async def call_without_agent_async(self, scope, receive, send, path):
        super().call_without_agent(path)
        return await self.asgi_app(scope, receive, send)
