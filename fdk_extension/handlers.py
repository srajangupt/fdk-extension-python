"""Request handlers."""
import datetime
import uuid

from sanic.blueprints import Blueprint
from sanic.response import json as json_response
from sanic.response import redirect

from fdk_extension.constants import SESSION_COOKIE_NAME
from fdk_extension.constants import SESSION_EXPIRY_IN_SECONDS
from fdk_extension.exceptions import FdkInvalidOAuthError
from fdk_extension.exceptions import FdkSessionNotFoundError
from fdk_extension.extension import extension
from fdk_extension.middleware.api_middleware import session_middleware
from fdk_extension.session.session import Session
from fdk_extension.session.session_storage import SessionStorage
from fdk_extension.utilities import logger

logger = logger.get_logger()


async def install_handler(request):
    try:
        company_id = int(request.args.get("company_id"))
        platform_config = await extension.get_platform_config(company_id)
        if extension.is_online_access_mode():
            session = Session(Session.generate_session_id(True))
        else:
            sid = Session.generate_session_id(False, **{
                "cluster": extension.cluster,
                "company_id": company_id
            })
            # await SessionStorage.delete_session(sid)
            session = await SessionStorage.get_session(sid)
            if not session:
                session = Session(sid)
            elif session.extension_id != extension.api_key:
                session = Session(sid)

        session_expires = datetime.datetime.now() + datetime.timedelta(seconds=SESSION_EXPIRY_IN_SECONDS)

        if session.is_new:
            session.company_id = company_id
            session.scope = extension.scopes
            session.expires = session_expires
            session.access_mode = extension.access_mode
            session.extension_id = extension.api_key

        request.conn_info.ctx.fdk_session = session
        request.conn_info.ctx.extension = extension

        company_cookie_name = "{}_{}".format(SESSION_COOKIE_NAME, company_id)

        session.state = str(uuid.uuid4())

        auth_callback = extension.get_auth_callback()

        # pass application id if received
        if request.args.get("application_id"):
            auth_callback += "?application_id=" + request.args.get("application_id")

        # start authorization flow
        redirect_url = await platform_config.oauthClient.startAuthorization({
            "scope": session.scope,
            "redirectUri": auth_callback,
            "state": session.state,
            "access_mode": extension.access_mode
        })

        logger.debug(f"Redirecting after install callback to url: {redirect_url}")

        next_response = redirect(redirect_url, headers={"x-company-id": str(company_id)})
        next_response.cookies[company_cookie_name] = session.session_id
        next_response.cookies[company_cookie_name]["domain"] = "0.0.0.0"
        # TODO : uncomment for production app
        # next_response.cookies[company_cookie_name]["secure"] = True
        # next_response.cookies[company_cookie_name]["samesite"] = "None"
        next_response.cookies[company_cookie_name]["httponly"] = False
        next_response.cookies[company_cookie_name]["expires"] = session.expires

        await SessionStorage.save_session(session)

        return next_response
    except Exception as e:
        logger.exception(e)
        return json_response({"error_message": str(e)}, 500)


async def auth_handler(request):
    try:
        if not request.conn_info.ctx.fdk_session:
            raise FdkSessionNotFoundError("Can not complete oauth process as session not found")

        if request.conn_info.ctx.fdk_session.state != request.args.get("state"):
            raise FdkInvalidOAuthError("Invalid oauth call")

        platform_config = await extension.get_platform_config(request.conn_info.ctx.fdk_session.company_id)
        await platform_config.oauthClient.verifyCallback(request.args)
        token = platform_config.oauthClient.raw_token

        session_expires = datetime.datetime.now() + datetime.timedelta(seconds=token["expires_in"])

        if extension.is_online_access_mode():
            request.conn_info.ctx.fdk_session.expires = session_expires
        else:
            request.conn_info.ctx.fdk_session.expires = None

        request.conn_info.ctx.fdk_session.access_token = token["access_token"]
        request.conn_info.ctx.fdk_session.expires_in = token["expires_in"]
        request.conn_info.ctx.fdk_session.access_token_validity = session_expires
        request.conn_info.ctx.fdk_session.current_user = token.get("current_user")
        request.conn_info.ctx.fdk_session.refresh_token = token.get("refresh_token")
        await SessionStorage.save_session(request.conn_info.ctx.fdk_session)
        request.conn_info.ctx.extension = extension

        redirect_url = await extension.callbacks["auth"](request)

        if extension.webhook_registry.is_initialized():
            client = await extension.get_platform_client(request.conn_info.ctx.fdk_session.company_id,
                                                         request.conn_info.ctx.fdk_session)
            await extension.webhook_registry.sync_events(client, None, True)

        company_cookie_name = "{}_{}".format(SESSION_COOKIE_NAME, request.conn_info.ctx.fdk_session.company_id)

        next_response = redirect(redirect_url, headers={"x-company-id": request.conn_info.ctx.fdk_session.company_id})
        next_response.cookies[company_cookie_name] = request.conn_info.ctx.fdk_session.session_id
        next_response.cookies[company_cookie_name]["httponly"] = True
        next_response.cookies[company_cookie_name]["expires"] = session_expires
        # TODO : uncomment for production app
        # next_response.cookies[company_cookie_name]["samesite"] = "None"
        # next_response.cookies[company_cookie_name]["secure"] = True
        logger.debug(f"Redirecting after auth callback to url: {redirect_url}")
        return next_response
    except Exception as e:
        logger.exception(e)
        return json_response({"error_message": str(e)}, 500)


async def uninstall_handler(request):
    try:
        client_id, company_id = request.json.get("client_id"), request.json["company_id"]
        if not extension.is_online_access_mode():
            sid = Session.generate_session_id(False, **{
                "cluster": extension.cluster,
                "company_id": company_id
            })
            session = await SessionStorage.get_session(sid)
            client = await extension.get_platform_client(company_id, session)
            request.conn_info.ctx.platformClient = client
        request.conn_info.ctx.extension = extension
        await extension.callbacks["uninstall"](request)
        return json_response({"success": True})
    except Exception as e:
        logger.exception(e)
        return json_response({"error_message": str(e)}, 500)


def setup_routes():
    fdk_routes_bp1 = Blueprint("fdk_routes_bp1")
    fdk_routes_bp2 = Blueprint("fdk_routes_bp2")

    fdk_routes_bp1.middleware(session_middleware, "request")
    fdk_routes_bp1.add_route(auth_handler, "/fp/auth")

    fdk_routes_bp2.add_route(install_handler, "/fp/install", methods=["GET"])
    fdk_routes_bp2.add_route(uninstall_handler, "/fp/uninstall", methods=["POST"])

    fdk_route = Blueprint.group(fdk_routes_bp1, fdk_routes_bp2)
    return fdk_route
