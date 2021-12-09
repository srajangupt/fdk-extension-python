import os
import sys

import aioredis
from sanic import Sanic
from sanic import response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)

from sanic_boilerplate import setup_fdk
from examples.extension_handlers import extension_handler

app = Sanic("test")

redis_connection = aioredis.from_url("redis://localhost")

base_url = "http://0.0.0.0:8000"

fdk_extension_client = setup_fdk({
    "api_key": "615476f46891c744b15826bd",
    "api_secret": "QGcx8kYiXd9qF01",
    "base_url": base_url,
    "scopes": ["company"],
    "callbacks": extension_handler,
    "storage": redis_connection,
    "access_mode": "offline",
    "cluster": "https://api.fyndx1.de"  # this is optional by default it points to prod.
})


@app.route("/_healthz")
def run(request):
    return response.text("Ok.")


async def test_route_handler(request):
    try:
        data = await request.conn_info.ctx.platform_client.lead.getTicket(id="61b08ec5c63045521bcf124f")
        return response.json({"data": data["json"]})
    except Exception as e:
        return response.json({"error_message": str(e)}, 500)


async def webhook_handler(request):
    try:
        company_id = request.args.get("companyId")
        client = await fdk_extension_client.get_platform_client(company_id)
        return response.json({"success": True})
    except Exception as e:
        return response.json({"error_message": str(e)}, 500)


app.blueprint(fdk_extension_client.fdk_blueprint)

fdk_extension_client.platform_api_routes_bp.add_route(test_route_handler, "/test/routes")

fdk_extension_client.application_proxy_routes_bp.add_route(test_route_handler, "/1234")

app.add_route(webhook_handler, "/webhook")

app.blueprint(fdk_extension_client.platform_api_routes_bp)
app.blueprint(fdk_extension_client.application_proxy_routes_bp)

# debug logs enabled with debug = True
app.run(host="0.0.0.0", port=8000, debug=True)
