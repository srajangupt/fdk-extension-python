# import fdk-client - python
from datetime import datetime
from typing import Dict
from urllib.parse import urljoin

from fdk_client.sdk.platform.PlatformClient import PlatformClient
from fdk_client.sdk.platform.PlatformConfig import PlatformConfig

from sanic_boilerplate.constants import FYND_CLUSTER
from sanic_boilerplate.constants import OFFLINE_ACCESS_MODE
from sanic_boilerplate.constants import ONLINE_ACCESS_MODE
from sanic_boilerplate.exceptions import FdkInvalidExtensionJson
from sanic_boilerplate.session.session import Session
from sanic_boilerplate.utilities.utility import is_valid_url


class Extension:
    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.storage = None
        self.base_url = None
        self.callbacks = None
        self.access_mode = None
        self.scopes = None
        self.cluster = FYND_CLUSTER

    def initialize(self, data: Dict):
        self.storage = data["storage"]

        if not data.get("api_key"):
            raise FdkInvalidExtensionJson("Invalid api_key")
        self.api_key = data["api_key"]

        if not data.get("api_secret"):
            raise FdkInvalidExtensionJson("Invalid api_secret")
        self.api_secret = data["api_secret"]

        if not is_valid_url(data["base_url"]):
            raise FdkInvalidExtensionJson("Invalid base_url")

        self.base_url = data["base_url"]
        self.scopes = self.verify_scopes(data["scopes"])

        if not data.get("callbacks") or (
                data["callbacks"] and (not data["callbacks"].get("auth") or not data["callbacks"].get("uninstall"))):
            raise FdkInvalidExtensionJson("Missing some of callbacks. Please add all `auth` and `uninstall` callbacks.")

        self.callbacks = data["callbacks"]
        self.access_mode = data.get("access_mode") or OFFLINE_ACCESS_MODE

        if data.get("cluster"):
            if not is_valid_url(data["cluster"]):
                raise FdkInvalidExtensionJson("Invalid cluster")
            self.cluster = data["cluster"]

    @staticmethod
    def verify_scopes(scopes):
        if not scopes:
            raise FdkInvalidExtensionJson("Invalid scopes in extension.json")
        return scopes

    def get_auth_callback(self):
        return urljoin(self.base_url, "/fp/auth")

    def is_online_access_mode(self):
        return self.access_mode == ONLINE_ACCESS_MODE

    async def get_platform_config(self, company_id):
        platform_config = PlatformConfig({
            "companyId": int(company_id),
            "domain": self.cluster,
            "apiKey": self.api_key,
            "apiSecret": self.api_secret
        })
        return platform_config

    async def get_platform_client(self, company_id, session: Session):
        platform_config = await self.get_platform_config(company_id)
        await platform_config.oauthClient.setToken({"expires_in": session.expires_in,
                                                    "access_token": session.access_token,
                                                    "refresh_token": session.refresh_token})
        if session.access_token_validity:
            ac_nr_expired = (session.access_token_validity - datetime.now()).total_seconds() <= 120
            if ac_nr_expired:
                res = await platform_config.oauthClient.renewAccessToken()

        return PlatformClient(platform_config)


class FdkExtensionClient:

    def __init__(self, **client_data):
        self.fdk_blueprint = client_data["fdk_blueprint"]
        self.extension = client_data["extension"]
        self.platform_api_routes_bp = client_data["platform_api_routes_bp"]
        self.application_proxy_routes_bp = client_data["application_proxy_routes_bp"]
        self.get_platform_client = client_data["get_platform_client"]
        self.get_application_client = client_data["get_application_client"]


extension = Extension()
