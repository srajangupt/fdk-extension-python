# FDK Extension Python
3.6+
FDK Extension Helper Python Library

Initial Setup

```python
import os
import sys

import aioredis
from sanic import Sanic
from sanic import response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)

from fdk-extension import setup_fdk
from examples.extension_handlers import extension_handler

app = Sanic("test")

redis_connection = aioredis.from_url("redis://localhost")

base_url = "http://0.0.0.0:8000"

fdk_extension_client = setup_fdk({
    "api_key": "<API_KEY>",
    "api_secret": "<API_SECRET>",
    "base_url": base_url,
    "scopes": ["company"],
    "callbacks": extension_handler,
    "storage": redis_connection,
    "access_mode": "offline",
    "cluster": "https://api.fyndx1.de",  # this is optional by default it points to prod.
})

app.blueprint(fdk_extension_client.fdk_blueprint)

fdk_extension_client.platform_api_routes_bp.add_route(test_route_handler, "/test/routes")

fdk_extension_client.application_proxy_routes_bp.add_route(test_route_handler, "/1234")

app.add_route(webhook_handler, "/webhook")

app.blueprint(fdk_extension_client.platform_api_routes_bp)
app.blueprint(fdk_extension_client.application_proxy_routes_bp)

# debug logs enabled with debug = True
app.run(host="0.0.0.0", port=8000, debug=True)

```

#### How to call platform apis?

To call platform api you need to have instance of `PlatformClient`. Instance holds methods for SDK classes. All routes registered under `platform_api_routes_bp` blueprint will have `platform_client` under request context object which is instance of `PlatformClient`.

> Here `platform_api_routes_bp` has middleware attached which allows passing such request which are called after launching extension under any company.

```python
async def test_route_handler(request):
    try:
        data = await request.conn_info.ctx.platform_client.lead.getTicket(id="61b08ec5c63045521bcf124f")
        return response.json({"data": data["json"]})
    except Exception as e:
        return response.json({"error_message": str(e)}, 500)
        
fdk_extension_client.platform_api_routes_bp.add_route(test_route_handler, "/test/routes")
app.blueprint(fdk_extension_client.platform_api_routes_bp)
```

#### How to call platform apis in background tasks?

Background tasks running under some consumer or webhook or under any queue can get platform client via method `get_platform_client`. It will return instance of `PlatformClient` as well. 

> Here FdkClient `access_mode` should be **offline**. Cause such client can only access PlatformClient in background task. 

```python
async def background_handler(request):
    try:
        company_id = request.args.get("companyId")
        client = await fdk_extension_client.get_platform_client(company_id)
        return response.json({"success": True})
    except Exception as e:
        return response.json({"error_message": str(e)}, 500)
```


#### How to register for webhook events?

Webhook events can be helpful to handle tasks when certan events occur on platform. You can subscribe to such events by passing webhook_config in setupFdk function.

```python
fdk_extension_client = setup_fdk({
    "api_key": "<API_KEY>",
    "api_secret": "<API_SECRET>",
    "base_url": base_url,
    "scopes": ["company"],
    "callbacks": extension_handler,
    "storage": redis_connection,
    "access_mode": "offline",
    "cluster": "https://api.fyndx1.de",  # this is optional by default it points to prod.
    "webhook_config": {
    "api_path": "/api/v1/webhooks", # required
    "notification_email": "test@abc.com", # required
    "subscribe_on_install": False, # optional. Default true
    "subscribed_saleschannel": "specific", #optional. Default all
    "event_map": {  # required
      'company/brand/create': {
        "version": '1',
        "handler": handleBrandCreate
      },
      'company/location/update': {
        "version": '1',
        "handler": handleLocationUpdate
      },
      'application/coupon/create': {
        "version": '1',
        "handler": handleCouponCreate
      }
    }
  }
})
```
> By default all webhook events all subscribed for all companies whenever they are installed. To disable this behavior set `subscribe_on_install` to `false`. If `subscribe_on_install` is set to false, you need to manually enable webhook event subscription by calling `syncEvents` method of `webhookRegistry`

There should be view on given api path to receive webhook call. It should be `POST` api path. Api view should call `processWebhook` method of `webhookRegistry` object available under `fdkClient` here.

> Here `processWebhook` will do payload validation with signature and calls individual handlers for event passed with webhook config. 

```python
async def webhook_handler(request):
    try:
        await fdk_extension_client.webhook_registry.process_webhook(request)
        return response.json({"success": True})
    except Exception as e:
        logger.exception(e)
        return response.json({"error_message": str(e), "success": False}, 500)

app.add_route(webhook_handler, "/webhook", methods=["POST"])
```

> Setting `subscribed_saleschannel` as "specific" means, you will have to manually subscribe saleschannel level event for individual saleschannel. Default value here is "all" and event will be subscribed for all sales channels. For enabling events manually use function `enableSalesChannelWebhook`. To disable receiving events for a saleschannel use function `disableSalesChannelWebhook`. 


##### How webhook registery subscribes to webhooks on Fynd Platform?
After webhook config is passed to setupFdk whenever extension is launched to any of companies where extension is installed or to be installed, webhook config data is used to create webhook subscriber on Fynd Platform for that company. 

> Any update to webhook config will not automatically update subscriber data on Fynd Platform for a company until extension is opened atleast once after the update. 

Other way to update webhook config manually for a company is to call `syncEvents` function of webhookRegistery.   