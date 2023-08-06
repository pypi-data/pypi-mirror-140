# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.middlewares.route_coverage.coverage_utils import CoverageUtils
from aiohttp.web_urldispatcher import DynamicResource


def create_aiohttp_routes(app):
    """
    Returns all the routes registered to a AioHttp app as a dict
    :param app: AioHttp app instance
    :return: dict {route_id:  RouteCoverage}
    """
    routes = {}

    for app_route in app.router._resources:
        for resource in app_route._routes:

            view_func = resource.handler
            name = view_func.__name__
            route = build_aiohttp_route(name, view_func)

            route_id = str(id(view_func))

            _route_attr = (
                app_route._formatter
                if isinstance(app_route, DynamicResource)
                else app_route._path
            )
            method_type = resource.method
            key = CoverageUtils.build_key(route_id, method_type)
            routes[key] = CoverageUtils.build_route_coverage(
                verb=method_type,
                url=CoverageUtils.get_normalized_uri(_route_attr),
                route=route,
            )

    return routes


def build_aiohttp_route(view_func_name, view_func):
    view_func_args = CoverageUtils.build_args_from_function(view_func)
    return view_func_name + view_func_args
