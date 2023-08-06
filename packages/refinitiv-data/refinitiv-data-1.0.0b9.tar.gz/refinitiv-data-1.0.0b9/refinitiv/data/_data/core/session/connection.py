import abc

from .auth_manager import AuthManager
from ...errors import PlatformSessionError


class SessionConnection(abc.ABC):
    def __init__(self, session):
        self._session = session

    async def open(self) -> bool:
        pass

    def close(self):
        pass


class DesktopConnection(SessionConnection):
    pass


class PlatformConnection(SessionConnection, abc.ABC):
    def get_omm_login_message(self):
        pass

    def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        pass


class RefinitivDataConnection(PlatformConnection):
    def __init__(self, session):
        PlatformConnection.__init__(self, session)
        self.auth_manager = AuthManager(session, auto_reconnect=session.server_mode)

    def get_omm_login_message(self) -> dict:
        return {
            "NameType": "AuthnToken",
            "Elements": {
                "AuthenticationToken": self._session._access_token,
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await self._session._http_request_async(
            url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )

    async def open(self) -> bool:
        return await self.auth_manager.authorize()

    def close(self):
        self.auth_manager.close()


class DeployedConnection(PlatformConnection):
    def get_omm_login_message(self):
        return {
            "Name": self._session._dacs_params.deployed_platform_username,
            "Elements": {
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

    async def http_request_async(self, *args, **kwargs):
        raise PlatformSessionError(
            -1,
            "Error!!! Platform session cannot connect to refinitiv dataplatform. "
            "Please check or provide the access right.",
        )

    async def open(self) -> bool:
        return True


class RefinitivDataAndDeployedConnection(DeployedConnection, RefinitivDataConnection):
    def __init__(self, session):
        DeployedConnection.__init__(self, session)
        RefinitivDataConnection.__init__(self, session)

    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await RefinitivDataConnection.http_request_async(
            self,
            url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )

    async def open(self) -> bool:
        return await RefinitivDataConnection.open(self)

    def close(self):
        RefinitivDataConnection.close(self)
