from sanic_boilerplate.api_blueprints import setup_proxy_routes_blueprint
from sanic_boilerplate.extension import FdkExtensionClient
from sanic_boilerplate.extension import extension
from sanic_boilerplate.handlers import setup_routes
from sanic_boilerplate.session.session import Session
from sanic_boilerplate.session.session_storage import SessionStorage

from fdk_client_python.sdk.application.ApplicationConfig import ApplicationConfig
from fdk_client_python.sdk.application.ApplicationClient import ApplicationClient


async def get_platform_client(company_id):
    client = None
    if not extension.is_online_access_mode():
        sid = Session.generate_session_id(False, **{
            "cluster": extension.cluster,
            "company_id": company_id
        })
        session = await SessionStorage.get_session(sid)
        client = await extension.get_platform_client(company_id, session)

    return client


async def get_application_client(application_id, application_token):
    application_config = ApplicationConfig({
        "applicationID": application_id,
        "applicationToken": application_token,
        "domain": extension.cluster
    })
    application_client = ApplicationClient(application_config)
    return application_client


def setup_fdk(data):
    extension.initialize(data)

    fdk_route = setup_routes()
    platform_api_routes_bp, application_proxy_routes_bp = setup_proxy_routes_blueprint()

    return FdkExtensionClient(**{
        "fdk_blueprint": fdk_route,
        "extension": extension,
        "platform_api_routes_bp": platform_api_routes_bp,
        "application_proxy_routes_bp": application_proxy_routes_bp,
        "get_platform_client": get_platform_client,
        "get_application_client": get_platform_client

    })
