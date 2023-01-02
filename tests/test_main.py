from pytest import MonkeyPatch
from unittest.mock import AsyncMock, Mock

from fdk_extension.extension import Extension
from fdk_extension.main import get_platform_client, get_application_client, setup_fdk
from fdk_extension.session.session import Session
from fdk_extension.session.session_storage import SessionStorage

from fdk_client.platform.PlatformClient import PlatformClient
from fdk_client.application.ApplicationClient import ApplicationClient

from .conftest import *

async def test_get_platform_client(extension_fixture: Extension, session_fixture: Session, monkeypatch: MonkeyPatch) -> None:
    extension_fixture.access_mode = OFFLINE_ACCESS_MODE

    mock_get_platform_client = AsyncMock(return_value=PlatformClient({}))
    mock_get_session = AsyncMock(return_value=session_fixture)
    monkeypatch.setattr(Extension, "get_platform_client", mock_get_platform_client)
    monkeypatch.setattr(SessionStorage, "get_session", mock_get_session)

    client = await get_platform_client(COMPANY_ID)

    mock_get_platform_client.assert_called_once_with(COMPANY_ID, session_fixture)
    mock_get_session.assert_called_once()
    assert isinstance(client, PlatformClient)
    assert extension_fixture.access_mode == OFFLINE_ACCESS_MODE


async def test_get_platform_client_negative(monkeypatch: MonkeyPatch) -> None:
    mock_access_mode = Mock(return_value=True)
    monkeypatch.setattr(Extension, "is_online_access_mode", mock_access_mode)

    client = await get_platform_client(COMPANY_ID)

    assert client == None


async def test_get_application_client() -> None:
    client = await get_application_client(APPLICATION_ID, APPLICATION_TOKEN)
    assert isinstance(client, ApplicationClient)