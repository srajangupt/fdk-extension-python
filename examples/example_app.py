import os
import sys

import aioredis
from sanic import Sanic, Blueprint
from sanic import response

import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fdk_extension import setup_fdk
from examples.extension_handlers import extension_handler
from fdk_extension.utilities.logger import get_logger
from fdk_extension.storage.redis_storage import RedisStorage

logger = get_logger()


app = Sanic("test")

redis_connection = aioredis.from_url("redis://localhost")

base_url = "http://0.0.0.0:8000"


async def handle_coupon_edit(event_name, payload, company_id, application_id):
    logging.debug(f"Event received for {company_id} and {application_id}")
    logging.debug(payload)


async def handle_product_event(event_name, payload, company_id):
    logging.debug(f"Event received for {company_id}")
    logging.debug(payload)


async def handle_sales_channel_product_event(event_name, payload, company_id, application_id):
    logging.debug(
        f"Event received for {company_id} and {application_id} and event_category {payload['event']['category']}")
    logging.debug(payload)


async def handle_location_event(event_name, payload, company_id):
    logging.debug(f"Event received for {company_id} and event_category {payload['event']['category']}")
    logging.debug(payload)


async def handle_ext_install(payload, company_id):
    logging.debug(f"Event received for {company_id}")
    logging.debug(payload)


fdk_extension_client = setup_fdk({
    "api_key": "6220daa4a5414621b975a41f",
    "api_secret": "EbeGBRC~Fthv5om",
    "base_url": base_url, # this is optional
    "scopes": ["company/product"], # this is optional
    "callbacks": extension_handler,
    "storage": RedisStorage(redis_connection),
    "access_mode": "offline",
    "debug": True,
    "cluster": "https://api.fyndx0.de",  # this is optional by default it points to prod.
    "webhook_config": {
        "api_path": "/webhook",
        "notification_email": "test2@abc.com",  # required
        "subscribed_saleschannel": "specific",  # optional
        "event_map": {  # required
            "application/coupon/update": {
                "version": '1',
                "handler": handle_coupon_edit
            },
            'company/location/update': {
                "version": '1',
                "handler": handle_location_event
            },
            "company/product/create": {
                "version": '1',
                "handler": handle_product_event
            },
            "application/product/create": {
                "version": '1',
                "handler": handle_sales_channel_product_event
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
        logger.exception(e)
        return response.json({"error_message": str(e)}, 500)


async def webhook_handler(request):
    try:
        await fdk_extension_client.webhook_registry.process_webhook(request)
        return response.json({"success": True})
    except Exception as e:
        logger.exception(e)
        return response.json({"error_message": str(e), "success": False}, 500)


async def enable_sales_channel_webhook_handler(request, application_id):
    try:
        await fdk_extension_client.webhook_registry.enable_sales_channel_webhook(request.conn_info.ctx.platform_client,
                                                                                 application_id)
        return response.json({"success": True})
    except Exception as e:
        logger.exception(e)
        return response.json({"error_message": str(e), "success": False}, 500)


async def disable_sales_channel_webhook_handler(request, application_id):
    try:
        await fdk_extension_client.webhook_registry.disable_sales_channel_webhook(request.conn_info.ctx.platform_client,
                                                                                  application_id)
        return response.json({"success": True})
    except Exception as e:
        logger.exception(e)
        return response.json({"error_message": str(e), "success": False}, 500)


app.blueprint(fdk_extension_client.fdk_route)

platform_bp = Blueprint("platform blueprint")
platform_bp.add_route(test_route_handler, "/test/routes")

application_bp = Blueprint("application blueprint")
application_bp.add_route(test_route_handler, "/1234")

app.add_route(webhook_handler, "/webhook", methods=["POST"])

platform_bp.add_route(enable_sales_channel_webhook_handler,
                                                      "/webhook/application/<application_id>/subscribe",
                                                      methods=["POST"])
platform_bp.add_route(disable_sales_channel_webhook_handler,
                                                      "/webhook/application/<application_id>/unsubscribe",
                                                      methods=["POST"])

fdk_extension_client.platform_api_routes.append(platform_bp)
fdk_extension_client.application_proxy_routes.append(application_bp)

app.blueprint(fdk_extension_client.platform_api_routes)
app.blueprint(fdk_extension_client.application_proxy_routes)

# debug logs enabled with debug = True
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
