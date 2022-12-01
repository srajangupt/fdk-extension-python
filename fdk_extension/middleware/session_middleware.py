from ..utilities import get_company_cookie_name
from ..session import SessionStorage

async def session_middleware(request):
    company_id = request.headers.get("x-company-id") or request.args.get("company_id")
    company_cookie_name = get_company_cookie_name(company_id=company_id)
    session_id = request.cookies.get(company_cookie_name)
    request.conn_info.ctx.fdk_session = await SessionStorage.get_session(session_id)