import pytest
from pytest import MonkeyPatch

from fdk_extension.extension import Extension
from fdk_extension.storage.redis_storage import RedisStorage
from fdk_extension.webhook import WebhookRegistry
from fdk_extension.session.session import Session

FYND_CLUSTER = "https://api.fynd.com"
ONLINE_ACCESS_MODE = "online"
OFFLINE_ACCESS_MODE = "offline"
SESSION_ID = "mock_session_id"
API_KEY = "mock_api_key"
API_SECRET = "mock_secret_key"
COMPANY_ID = int(999)
BASE_URL = "https://abc.com"
APPLICATION_ID = "mock_application_id"
APPLICATION_TOKEN = "mock_application_token"

@pytest.fixture()
def extension_fixture(webhook_registry_fixture: WebhookRegistry) -> Extension:
    extension =  Extension()
    extension.api_key = API_KEY
    extension.api_secret = API_SECRET
    extension.storage = None
    extension.base_url = BASE_URL
    extension.callbacks = None
    extension.access_mode = ONLINE_ACCESS_MODE
    extension.scopes = ["company/profile", "company/order", "company/product"]
    extension.cluster = FYND_CLUSTER
    extension.webhook_registry = webhook_registry_fixture
    extension._Extension__is_initialized = True
    return extension


@pytest.fixture()
def webhook_registry_fixture():
    return WebhookRegistry()


@pytest.fixture()
def extension_data_fixture() -> dict:
    return {
        'url': 'https://api.fynd.com/service/panel/partners/v1.0/extensions/details/mock_api_key', 
        'method': 'GET', 
        'payload': None,
        'status_code': 200, 
        'headers': {
            'Content-Type': 'application/json; charset=utf-8', 
            'X-Fynd-Trace-Id': '4a9785855a8c3596f71be0e36b3fee65'
        }, 
        'json': {
            'name': 'test 123', 
            'extention_type': 'private', 
            'base_url': BASE_URL, 
            'scope': [
                'company/profile', 
                'company/saleschannel', 
                'company/product', 
                'company/order', 
                'company/application/customer', 
                'company/application/analytics', 
                'company/application/storage', 
                'company/application/marketing', 
                'company/application/catalogue', 
                'company/application/communication', 
                'company/application/support', 
                'company/application/order', 
                'company/application/settings'
            ]
        }
    }


@pytest.fixture()
def session_fixture() -> Session:
    session = Session(SESSION_ID, False)
    session.access_mode = OFFLINE_ACCESS_MODE
    return session


{
    'url': 'https://api.fyndx0.de/service/panel/partners/v1.0/extensions/details/6332e8ce419d82451197c1be', 
    'method': 'GET', 
    'payload': None, 
    'external_call_request_time': '2022-12-19 17:28:42.646853+05:30', 
    'status_code': 200, 
    'headers': {
        'Date': 'Mon, 19 Dec 2022 11:58:42 GMT', 
        'Content-Type': 'application/json; charset=utf-8', 
        'Content-Length': '464', 
        'Connection': 'keep-alive', 
        'Strict-Transport-Security': 'max-age=63072000; includeSubdomains', 
        'X-Content-Type-Options': 'nosniff', 
        'X-Powered-By': 'Express', 
        'Etag': 'W/"1d0-yrxIinM2gSQCL0l+XyVtwRBgLZU"', 
        'X-Fynd-Trace-Id': '4a9785855a8c3596f71be0e36b3fee65'
    }, 
    'cookies': {}, 
    'error_message': '', 
    'latency': 0.08759403228759766, 
    'json': {
        'name': 'test 123', 
        'extention_type': 'private', 
        'base_url': 'https://cc6b-27-109-3-234.in.ngrok.io', 
        'scope': [
            'company/profile', 
            'company/saleschannel', 
            'company/product', 
            'company/order', 
            'company/application/customer', 
            'company/application/analytics', 
            'company/application/storage', 
            'company/application/marketing', 
            'company/application/catalogue', 
            'company/application/communication', 
            'company/application/support', 
            'company/application/order', 
            'company/application/settings'
        ]
    }
}