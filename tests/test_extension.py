import pytest
from pytest import MonkeyPatch
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from .conftest import *

from fdk_extension.extension import Extension
from fdk_extension.exceptions import FdkInvalidConfig
from fdk_extension.session.session import Session
from fdk_extension.session.session_storage import SessionStorage

from fdk_client.platform.PlatformConfig import PlatformConfig
from fdk_client.platform.PlatformClient import PlatformClient
from fdk_client.platform.OAuthClient import OAuthClient
from fdk_client.common.aiohttp_helper import AiohttpHelper



async def test_initialize(extension_data_fixture: dict, monkeypatch: MonkeyPatch) -> None:
    extension = Extension()
    data_to_pass = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "base_url": BASE_URL,
        "callbacks": {
            "auth": Mock(),
            "uninstall": Mock()
        },
        "scopes": extension_data_fixture["json"]['scope'],
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": FYND_CLUSTER,
        'webhook_config': {""}
    }

    mock_webhook_initialize = AsyncMock()
    mock_get_extension_details = AsyncMock(return_value=extension_data_fixture["json"])
    monkeypatch.setattr(WebhookRegistry, "initialize", mock_webhook_initialize)
    monkeypatch.setattr(Extension, "get_extension_details", mock_get_extension_details)

    await extension.initialize(data=data_to_pass)

    assert extension.api_key == API_KEY
    assert extension.api_secret == API_SECRET
    assert extension.base_url == BASE_URL
    assert extension.cluster == FYND_CLUSTER
    assert extension.access_mode == OFFLINE_ACCESS_MODE
    assert extension.callbacks == data_to_pass["callbacks"]
    assert extension.scopes == extension_data_fixture['json']['scope']
    assert extension._Extension__is_initialized
    mock_webhook_initialize.assert_called_once_with(data_to_pass["webhook_config"], data_to_pass)
    mock_get_extension_details.assert_called_once()


async def test_initialize_api_key_missing() -> None:
    extension = Extension()
    data_to_pass = {
        "api_secret": API_SECRET,
        "base_url": BASE_URL,
        "callbacks": {
            "auth": Mock(),
            "uninstall": Mock()
        },
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": FYND_CLUSTER,
    }
    with pytest.raises(FdkInvalidConfig, match="Invalid api_key"):
        await extension.initialize(data_to_pass)


async def test_initialize_api_secret_mission() -> None:
    extension = Extension()
    data_to_pass = {
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "callbacks": {
            "auth": Mock(),
            "uninstall": Mock()
        },
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": FYND_CLUSTER,
    }
    with pytest.raises(FdkInvalidConfig, match="Invalid api_secret"):
        await extension.initialize(data_to_pass)


async def test_initialize_callbacks_missing() -> None:
    extension = Extension()
    data_to_pass = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "base_url": BASE_URL,
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": FYND_CLUSTER,
    }
    with pytest.raises(FdkInvalidConfig, match="Missing some of callbacks. Please add all `auth` and `uninstall` callbacks."):
        await extension.initialize(data_to_pass)


async def test_initialize_invalid_cluster() -> None:
    extension = Extension()
    data_to_pass = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "base_url": BASE_URL,
        "callbacks": {
            "auth": Mock(),
            "uninstall": Mock()
        },
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": "invalid_url",
    }
    with pytest.raises(FdkInvalidConfig, match="Invalid cluster"):
        await extension.initialize(data_to_pass)


async def test_initialize_invalid_base_url(extension_data_fixture: dict, monkeypatch: MonkeyPatch) -> None:
    extension = Extension()
    data_to_pass = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "base_url": "invalid_base_url",
        "callbacks": {
            "auth": Mock(),
            "uninstall": Mock()
        },
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": FYND_CLUSTER,
    }
    mock_get_extension_details = AsyncMock(return_value=extension_data_fixture["json"])
    with pytest.raises(FdkInvalidConfig, match="Invalid base_url value. Invalid value: \w"):
        monkeypatch.setattr(Extension, "get_extension_details", mock_get_extension_details)
        await extension.initialize(data_to_pass)

    mock_get_extension_details.assert_called_once()


async def test_initialize_not_passed_base_url(extension_data_fixture: dict, monkeypatch: MonkeyPatch) -> None:
    extension = Extension()
    data_to_pass = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "callbacks": {
            "auth": Mock(),
            "uninstall": Mock()
        },
        "storage": Mock(),
        "access_mode": OFFLINE_ACCESS_MODE,
        "cluster": FYND_CLUSTER,
    }
    mock_get_extension_details = AsyncMock(return_value=extension_data_fixture["json"])
    monkeypatch.setattr(Extension, "get_extension_details", mock_get_extension_details)

    await extension.initialize(data_to_pass)

    mock_get_extension_details.assert_called_once()
    assert extension.base_url == BASE_URL


def test_is_online_access_mode(extension_fixture: Extension) -> None:
    assert extension_fixture.is_online_access_mode()

def test_is_online_access_mode_negative(extension_fixture: Extension) ->  None:
    extension_fixture.access_mode = OFFLINE_ACCESS_MODE
    assert not extension_fixture.is_online_access_mode()

def test_is_initialized(extension_fixture: Extension) -> None:
    assert extension_fixture.is_initialized()

def test_verify_scopes_negative(extension_fixture: Extension, extension_data_fixture: dict) -> None:
    extension_data_fixture["json"]["scope"] = ['company/profile', 'company/product']
    with pytest.raises(FdkInvalidConfig):
        extension_fixture.verify_scopes(extension_fixture.scopes, extension_data_fixture["json"])

def test_verify_scopes(extension_fixture: Extension, extension_data_fixture: dict) -> None:
    scopes = extension_fixture.verify_scopes(extension_fixture.scopes, extension_data_fixture["json"])
    assert scopes == extension_fixture.scopes

def test_get_auth_callback(extension_fixture: Extension) -> None:
    expected_data = f"{extension_fixture.base_url}/fp/auth"
    data = extension_fixture.get_auth_callback()
    assert data == expected_data

def test_get_platform_config(extension_fixture: Extension) -> None:
    data = extension_fixture.get_platform_config(COMPANY_ID)
    assert data.apiKey == extension_fixture.api_key
    assert data.apiSecret == extension_fixture.api_secret
    assert data.companyId == COMPANY_ID
    assert data.domain == FYND_CLUSTER
    assert data.useAutoRenewTimer == False
    assert isinstance(data, PlatformConfig)

def test_get_platform_config_negative(extension_fixture: Extension) -> None:
    extension_fixture._Extension__is_initialized = False
    with pytest.raises(FdkInvalidConfig):
        extension_fixture.get_platform_config(COMPANY_ID)

async def test_get_platform_client_negative(extension_fixture: Extension, session_fixture: Session) -> None:
    extension_fixture._Extension__is_initialized = False
    with pytest.raises(FdkInvalidConfig):
        await extension_fixture.get_platform_client(COMPANY_ID, session_fixture)

async def test_get_platform_client(extension_fixture: Extension, session_fixture: Session, monkeypatch: MonkeyPatch) -> None:

    mock_setTokenFromSession = Mock()
    monkeypatch.setattr(OAuthClient, "setTokenFromSession", mock_setTokenFromSession)

    client = await extension_fixture.get_platform_client(COMPANY_ID, session_fixture)

    assert isinstance(client, PlatformClient)

    mock_setTokenFromSession.assert_called_once()
    for item in client._conf.extraHeaders:
        if "x-ext-lib-version" in item.keys():
            return
    assert False


async def test_get_platform_client_refresh_token(extension_fixture: Extension, session_fixture: Session, monkeypatch: MonkeyPatch) -> None:

    mock_setTokenFromSession = Mock()
    mock_renewAccessToken = AsyncMock()
    mock_update_token = Mock()
    mock_save_session = AsyncMock()
    monkeypatch.setattr(OAuthClient, "setTokenFromSession", mock_setTokenFromSession)
    monkeypatch.setattr(OAuthClient, "renewAccessToken", mock_renewAccessToken)
    monkeypatch.setattr(Session, "update_token", mock_update_token)
    monkeypatch.setattr(SessionStorage, "save_session", mock_save_session)
    session_fixture.access_token_validity = int(datetime.timestamp(datetime.now() + timedelta(minutes=1)))
    session_fixture.refresh_token = "mock_refresh_token"

    client = await extension_fixture.get_platform_client(COMPANY_ID, session_fixture)

    assert isinstance(client, PlatformClient)
    mock_setTokenFromSession.assert_called_once()
    mock_renewAccessToken.assert_called_once_with(True)
    mock_update_token.assert_called_once()
    mock_save_session.assert_called_once()
    for item in client._conf.extraHeaders:
        if "x-ext-lib-version" in item.keys():
            return
    assert False


async def test_get_extension_details(extension_fixture: Extension, extension_data_fixture: dict, monkeypatch: MonkeyPatch) -> None:

    mock_aiohttp_request = AsyncMock(return_value=extension_data_fixture)
    monkeypatch.setattr(AiohttpHelper, "aiohttp_request", mock_aiohttp_request)

    data = await extension_fixture.get_extension_details()

    assert data == extension_data_fixture["json"]
    mock_aiohttp_request.assert_called_once()


async def test_get_extension_details_negative(extension_fixture: Extension, extension_data_fixture: dict, monkeypatch: MonkeyPatch) -> None:

    with pytest.raises(FdkInvalidConfig):
        extension_data_fixture["status_code"] = 400
        extension_data_fixture["json"]["message"] = "Error Message"

        mock_aiohttp_request = AsyncMock(return_value=extension_data_fixture)
        monkeypatch.setattr(AiohttpHelper, "aiohttp_request", mock_aiohttp_request)
        
        await extension_fixture.get_extension_details()