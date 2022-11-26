"""Setup fdk file."""
from fdk_client.application.ApplicationClient import ApplicationClient
from fdk_client.application.ApplicationConfig import ApplicationConfig

from fdk_extension.api_blueprints import setup_proxy_routes_blueprint
from fdk_extension.extension import FdkExtensionClient
from fdk_extension.extension import extension
from fdk_extension.handlers import setup_routes
from fdk_extension.session.session import Session
from fdk_extension.session.session_storage import SessionStorage


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
        "webhook_registry": extension.webhook_registry,
        "application_proxy_routes_bp": application_proxy_routes_bp,
        "get_platform_client": get_platform_client,
        "get_application_client": get_application_client

    })
