import os
import sys

import aioredis
from sanic import Sanic
from sanic import response

import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)

from sanic_boilerplate import setup_fdk
from examples.extension_handlers import extension_handler

app = Sanic("test")

redis_connection = aioredis.from_url("redis://localhost")

base_url = "http://0.0.0.0:8000"


async def handle_ext_install(payload, company_id):
    logging.debug(f"Event received for {company_id}")
    logging.debug(payload)


async def handle_coupon_edit(payload, company_id, application_id):
    logging.debug(f"Event received for {company_id} and ${application_id}")
    logging.debug(payload)


fdk_extension_client = setup_fdk({
    "api_key": "615476f46891c744b15826bd",
    "api_secret": "QGcx8kYiXd9qF01",
    "base_url": base_url,
    "scopes": ["company"],
    "callbacks": extension_handler,
    "storage": redis_connection,
    "access_mode": "offline",
    "debug": True,
    "cluster": "https://api.fyndx1.de",  # this is optional by default it points to prod.
    "webhook_config": {
        "api_path": "/webhook",
        "notification_email": "test2@abc.com",  # required
        "subscribed_saleschannel": "specific",  # optional
        "event_map": {  # required
            "extension/install": {
                "handler": handle_ext_install
            },
            "coupon/update": {
                "handler": handle_coupon_edit
            }
        }
    }
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
    await fdk_extension_client.webhook_registry.process_webhook(request)
    return response.json({"success": True})


async def enable_sales_channel_webhook_handler(request, application_id):
    await fdk_extension_client.webhook_registry.enable_sales_channel_webhook(request.conn_info.ctx.platform_client,
                                                                             application_id)
    return response.json({"success": True})


async def disable_sales_channel_webhook_handler(request, application_id):
    await fdk_extension_client.webhook_registry.disable_sales_channel_webhook(request.conn_info.ctx.platform_client,
                                                                              application_id)
    return response.json({"success": True})


app.blueprint(fdk_extension_client.fdk_blueprint)

fdk_extension_client.platform_api_routes_bp.add_route(test_route_handler, "/test/routes")

fdk_extension_client.application_proxy_routes_bp.add_route(test_route_handler, "/1234")

app.add_route(webhook_handler, "/webhook", methods=["POST"])

fdk_extension_client.platform_api_routes_bp.add_route(enable_sales_channel_webhook_handler,
                                                      "/webhook/application/<application_id>/subscribe",
                                                      methods=["POST"])
fdk_extension_client.platform_api_routes_bp.add_route(disable_sales_channel_webhook_handler,
                                                      "/webhook/application/<application_id>/unsubscribe",
                                                      methods=["POST"])

app.blueprint(fdk_extension_client.platform_api_routes_bp)
app.blueprint(fdk_extension_client.application_proxy_routes_bp)

# debug logs enabled with debug = True
app.run(host="0.0.0.0", port=8000, debug=True)
