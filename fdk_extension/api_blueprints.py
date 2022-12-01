from sanic import Blueprint

from .middleware.api_middleware import application_proxy_on_request
from .middleware.api_middleware import platform_api_on_request
from .middleware.session_middleware import session_middleware


def setup_proxy_routes() -> tuple(Blueprint, Blueprint):
    platform_api_routes = Blueprint("platform_api_routes_bp")
    platform_api_routes.middleware(session_middleware, "request")
    platform_api_routes.middleware(platform_api_on_request, "request")

    application_proxy_routes = Blueprint("application_proxy_routes_bp")
    application_proxy_routes.middleware(application_proxy_on_request, "request")

    return platform_api_routes, application_proxy_routes
