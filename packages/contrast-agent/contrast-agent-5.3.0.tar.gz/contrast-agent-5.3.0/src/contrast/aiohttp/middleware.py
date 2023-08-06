# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

import contrast

from aiohttp.web import Response, StreamResponse
from aiohttp.web_urldispatcher import DynamicResource

from contrast.aiohttp import sources
from contrast.agent.request_context import RequestContext
from contrast.agent import scope
from contrast.agent.middlewares.route_coverage.aiohttp_routes import (
    create_aiohttp_routes,
    build_aiohttp_route,
)
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.extern import structlog as logging
from contrast.utils.decorators import log_time_cm, cached_property
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.response_wrappers.aiohttp_response_wrapper import (
    AioHttpResponseWrapper,
)

from contrast.utils.decorators import fail_safely
from contrast.utils import Profiler

logger = logging.getLogger("contrast")


class AioHttpMiddleware(BaseMiddleware):
    __middleware_version__ = 1  # Aiohttp new-style middleware

    # Since there is no way to get the `app` instance, on startup of AioHttp,
    # until the first request, hence we will not have `app` finder logic.
    def __init__(self, app_name: str = None) -> None:
        self.app = None
        self.app_name = app_name
        super().__init__()

    async def __call__(self, request, handler) -> StreamResponse:
        self.app = request.app

        path = sources.get_path_query(request.message)

        with Profiler(path[0]):
            if self.is_agent_enabled():
                if self.settings.ignore_request(path[0]):
                    return await self.call_without_agent_async(
                        request, handler, path[0]
                    )

                with scope.contrast_scope():
                    environ = await sources.aiohttp_request_to_environ(request)

                context = RequestContext(environ)

                with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                    return await self.call_with_agent(
                        context, request, handler, path[0]
                    )

            return await self.call_without_agent_async(request, handler, path[0])

    async def call_with_agent(
        self, context, request, handler, path: str
    ) -> StreamResponse:
        self.log_start_request_analysis(path[0])

        sources.track_aiohttp_request_sources(context, request)

        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                response = await handler(request)

            with scope.contrast_scope():
                wrapped_response = AioHttpResponseWrapper(response)

            context.extract_response_to_context(wrapped_response)

            self.postfilter(context)

            self.check_for_blocked(context)
            return response

        except ContrastServiceException as e:
            logger.warning(e)
            return await self.call_without_agent_async(request, handler)
        except Exception as e:
            response = self.handle_exception(e)
            return response
        finally:
            self.handle_ensure(context, request)
            self.log_end_request_analysis(path[0])
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    async def call_without_agent_async(self, request, handler, path) -> StreamResponse:
        super().call_without_agent(path)
        return await handler(request)

    @fail_safely("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_aiohttp_routes(self.app)

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_aiohttp_route(url, view_func)

    @fail_safely("Unable to get view func")
    def get_view_func(self, request):
        path = sources.get_path_query(request.message)
        view_func = None

        # This approach has at worst O(_resources) performance
        # but it's a first attempt at implementing a sync
        # version of aiohttp.web_urldispatches.UrlDispatcher.resolve
        for app_route in self.app.router._resources:
            _app_route = (
                app_route._formatter
                if isinstance(app_route, DynamicResource)
                else app_route._path
            )
            if _app_route == path[0]:
                routes = app_route._routes
                for route in routes:
                    if route.method == request.method:
                        return route.handler

        return view_func

    def generate_security_exception_response(self):
        return Response(
            text=self.OVERRIDE_MESSAGE,
            status=SecurityException.STATUS_CODE,
            content_type="text/html",
        )

    @cached_property
    def trigger_node(self):
        """
        Used by reflected xss postfilter rule
        """
        method_name = self.app_name

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.app
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )
