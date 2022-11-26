import json

from fdk_client.application.ApplicationClient import ApplicationClient
from fdk_client.application.ApplicationConfig import ApplicationConfig
from sanic.response import json as json_response

from fdk_extension.constants import SESSION_COOKIE_NAME
from fdk_extension.extension import extension
from fdk_extension.session.session_storage import SessionStorage


async def session_middleware(request):
    company_id = request.headers.get("x-company-id") or request.args.get("company_id") or 1
    company_cookie_name = "{}_{}".format(SESSION_COOKIE_NAME, company_id)
    session_id = request.cookies.get(company_cookie_name)
    request.conn_info.ctx.fdk_session = await SessionStorage.get_session(session_id)


async def application_proxy_on_request(request):
    if request.headers.get("x-user-data"):
        request.conn_info.ctx.user = json.loads(request.headers["x-user-data"])
    if request.headers.get("x-application-data"):
        request.conn_info.ctx.application = json.loads(request.headers["x-application-data"])
        request.conn_info.ctx.application_config = ApplicationConfig({
            "applicationID": request.conn_info.ctx.application._id,
            "applicationToken": request.conn_info.ctx.application.token,
        })
        request.conn_info.ctx.application_client = ApplicationClient(request.conn_info.ctx.application_config)


async def platform_api_on_request(request):
    if not request.conn_info.ctx.fdk_session:
        return json_response({"message": "unauthorized"}, status=401)
    client = await extension.get_platform_client(request.conn_info.ctx.fdk_session.company_id,
                                                 request.conn_info.ctx.fdk_session)
    request.conn_info.ctx.platform_client = client
    request.conn_info.ctx.extension = extension
