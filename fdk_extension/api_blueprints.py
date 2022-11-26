from sanic import Blueprint

from fdk_extension.middleware.api_middleware import application_proxy_on_request
from fdk_extension.middleware.api_middleware import platform_api_on_request
from fdk_extension.middleware.api_middleware import session_middleware


def setup_proxy_routes_blueprint():
    platform_api_routes_bp = Blueprint("platform_api_routes_bp")
    platform_api_routes_bp.middleware(session_middleware, "request")
    platform_api_routes_bp.middleware(platform_api_on_request, "request")

    application_proxy_routes_bp = Blueprint("application_proxy_routes_bp")
    application_proxy_routes_bp.middleware(application_proxy_on_request, "request")

    return platform_api_routes_bp, application_proxy_routes_bp
