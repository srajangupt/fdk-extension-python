"""Extension class file."""
from typing import Dict
from urllib.parse import urljoin
import base64, json

from fdk_client.platform.PlatformClient import PlatformClient
from fdk_client.platform.PlatformConfig import PlatformConfig
from fdk_client.common.utils import get_headers_with_signature
from fdk_client.common.aiohttp_helper import AiohttpHelper

from fdk_extension.constants import FYND_CLUSTER
from fdk_extension.constants import OFFLINE_ACCESS_MODE
from fdk_extension.constants import ONLINE_ACCESS_MODE
from fdk_extension.exceptions import FdkInvalidExtensionJson
from fdk_extension.session import Session, SessionStorage
from fdk_extension.utilities.logger import get_logger
from fdk_extension.utilities import is_valid_url, get_current_timestamp
from fdk_extension.webhook import WebhookRegistry

logger = get_logger()


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
        self.webhook_registry = None
        self.__is_initialized = False

    def initialize(self, data: Dict):
        self.__is_initialized = False

        self.storage = data["storage"]

        # API Key
        if not data.get("api_key"):
            raise FdkInvalidExtensionJson("Invalid api_key")
        self.api_key = data["api_key"]

        # API Secret
        if not data.get("api_secret"):
            raise FdkInvalidExtensionJson("Invalid api_secret")
        self.api_secret = data["api_secret"]

        # Callbacks
        if (not data.get("callbacks") or (data.get("callbacks") and (not data["callbacks"].get("auth") or not data["callbacks"].get("uninstall")))):
            raise FdkInvalidExtensionJson("Missing some of callbacks. Please add all `auth` and `uninstall` callbacks.")
        self.callbacks = data["callbacks"]

        # Access Mode
        self.access_mode = data.get("access_mode") or OFFLINE_ACCESS_MODE

        # Cluster
        if data.get("cluster"):
            if not is_valid_url(data["cluster"]):
                raise FdkInvalidExtensionJson("Invalid cluster")
            self.cluster = data["cluster"]

        # Webhook Registry
        self.webhook_registry = WebhookRegistry()

        # Fetching Extesnion data
        extension_data = self.get_extension_details()

        # base url
        if (data.get("base_url") and not is_valid_url(data.get("base_url"))):
            raise FdkInvalidExtensionJson(f"Invalid base_url value. Invalid value: {data.get('base_url')}")
        elif (not data.get("base_url")):
            data["base_url"] = extension_data.get("base_url")
        self.base_url = data["base_url"]

        # scopes
        if (data.get("scopes")):
            data["scopes"] = self.verify_scopes(data["scopes"], extension_data)
        self.scopes = data["scopes"] or extension_data["scope"]

        logger.debug("Extension initialized")

        if data.get("webhook_config"):
            self.webhook_registry.initialize(data["webhook_config"], data)

        self.__is_initialized = True


    def is_initialized(self):
        return self.__is_initialized


    def verify_scopes(scopes, extension_data):
        missing_scopes = [scope for scope in scopes if scope not in extension_data]
        if (not scopes or len(scopes) <= 0 or len(missing_scopes)):
            raise FdkInvalidExtensionJson(f"Invalid scopes in extension config. Invalid scopes: {', '.join(missing_scopes)}")
        return scopes

    def get_auth_callback(self):
        return urljoin(self.base_url, "/fp/auth")

    def is_online_access_mode(self):
        return self.access_mode == ONLINE_ACCESS_MODE

    def get_platform_config(self, company_id):
        if (not self.is_initialized()):
            raise FdkInvalidExtensionJson("Extension not initialized due to invalid data")

        platform_config = PlatformConfig({
            "companyId": int(company_id),
            "domain": self.cluster,
            "apiKey": self.api_key,
            "apiSecret": self.api_secret,
            "useAutoRenewTimer": False
        })
        return platform_config


    async def get_platform_client(self, company_id, session: Session):
        if (not self.is_initialized()):
            raise FdkInvalidExtensionJson("Extension not initialized due to invalid data")

        platform_config = self.get_platform_config(company_id)
        platform_config.oauthClient.setToken(session)
        platform_config.oauthClient.token_expires_at = session.access_token_validity

        if (session.access_token_validity and session.refresh_token):
            ac_nr_expired = (session.access_token_validity - get_current_timestamp() // 1000) <= 120
            if ac_nr_expired:
                logger.debug(f"Renewing access token for company {company_id} with platform config {json.dumps(platform_config)}") # TODO: Safe stringfy json object
                renew_token_res = await platform_config.oauthClient.renewAccessToken(session.access_mode == OFFLINE_ACCESS_MODE)
                renew_token_res["access_token_validity"] = platform_config.oauthClient.token_expires_at
                session.update_token(renew_token_res)
                await SessionStorage.save_session(session)
                logger.debug(f"Access token renewed for comapny {company_id} with response {renew_token_res}")

        platform_client = PlatformClient(platform_config)
        # TODO: add x-ext-lib-version headers
        # platform_client.setExtraHeaders({
        #     'x-ext-lib-version': f"py/{__version__}"
        # })
        return platform_client


    # Making API request to fetch extension details
    async def get_extension_details(self):
        try:
            url = f"{self.cluster}/service/panel/partners/v1.0/extensions/details/{self.api_key}"
            token = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()
            headers = {
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
                # TODO: add x-ext-lib-version headers
            }
            headers = await get_headers_with_signature(
                domain=self.cluster,
                method="get",
                url=url,
                query_string="",
                headers=headers,
                exclude_headers=["Authorization"]
            )
            reponse = await AiohttpHelper().aiohttp_request(request_type="GET", url=url, headers=headers)
            return reponse["json"]
        except Exception as e:
            raise FdkInvalidExtensionJson(f"Invalid api_key or api_secret. Reason: {str(e)}")


class FdkExtensionClient:

    def __init__(self, **client_data):
        self.fdk_blueprint = client_data["fdk_blueprint"]
        self.extension = client_data["extension"]
        self.platform_api_routes_bp = client_data["platform_api_routes_bp"]
        self.application_proxy_routes_bp = client_data["application_proxy_routes_bp"]
        self.get_platform_client = client_data["get_platform_client"]
        self.get_application_client = client_data["get_application_client"]
        self.webhook_registry = client_data["webhook_registry"]


extension = Extension()
