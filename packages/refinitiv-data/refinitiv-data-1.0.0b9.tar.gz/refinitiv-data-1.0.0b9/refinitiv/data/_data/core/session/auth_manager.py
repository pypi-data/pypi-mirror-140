import asyncio
import time
from typing import TYPE_CHECKING, Optional, Union, Callable

from eventemitter import EventEmitter

from ._default_session_manager import Wrapper
from .access_token_updater import AccessTokenUpdater
from .event import UpdateEvent
from .refresh_token_updater import RefreshTokenUpdater
from .tools import MINUTES_10, get_delays, handle_exception, Daemon
from ..log_reporter import LogReporter
from ...tools import cached_property

if TYPE_CHECKING:
    from . import PlatformSession

DEFAULT_EXPIRES_IN_SEC = MINUTES_10
DEFAULT_LATENCY_SEC = 20

delays = get_delays()


class TokenInfo:
    def __init__(
        self,
        access_token: str,
        expires_in: Union[float, str, int],
        scope: Optional[str] = "",
        token_type: Optional[str] = "",
        refresh_token: Optional[str] = "",
    ) -> None:
        super().__init__()
        self.token_type = token_type
        self.scope = scope
        self.refresh_token = refresh_token

        try:
            expires_in = float(expires_in)
            if expires_in < DEFAULT_EXPIRES_IN_SEC:
                expires_in = DEFAULT_EXPIRES_IN_SEC
        except Exception:
            expires_in = DEFAULT_EXPIRES_IN_SEC

        self.expires_in = float(expires_in)
        self.expires_at = time.time() + expires_in

        self.access_token = access_token

    def calc_expires_in(self, latency: float) -> int:
        if latency > DEFAULT_LATENCY_SEC:
            latency = DEFAULT_LATENCY_SEC

        expires_secs = self.expires_in // 2

        if expires_secs - latency > 0:
            expires_secs = expires_secs - latency

        return int(expires_secs)


def create_token_info(json_content: dict) -> TokenInfo:
    token_info = TokenInfo(
        access_token=json_content["access_token"],
        refresh_token=json_content["refresh_token"],
        expires_in=json_content.get("expires_in", ""),
        scope=json_content.get("scope", ""),
        token_type=json_content.get("token_type", ""),
    )
    return token_info


class AuthManager(LogReporter):
    """
    Methods
    -------
    is_closed()
        The method returns True if closed, otherwise False

    is_authorized()
        The method returns True if authorized, otherwise False.
        If instance destroyed or closed always returns False

    authorize()
        The method starts process authorization

    close()
        The method stops refresh token updater and access token updater

    dispose()
        The method destroy an instance

    """

    _daemon: Optional[Daemon] = None

    def __init__(self, session: "PlatformSession", auto_reconnect: bool) -> None:
        LogReporter.__init__(self, logger=session)

        self._session = session
        self._auto_reconnect = auto_reconnect

        self._emitter: EventEmitter = EventEmitter()
        self._token_info: Wrapper = Wrapper[TokenInfo]()
        self._closed: bool = False
        self._authorized: bool = False

    @cached_property
    def _access_token_updater(self) -> AccessTokenUpdater:
        return AccessTokenUpdater(
            self._session, 0.00001, self._access_token_update_handler
        )

    @cached_property
    def _refresh_token_updater(self) -> RefreshTokenUpdater:
        return RefreshTokenUpdater(
            self._session,
            self._token_info,
            0.00001,
            self._refresh_token_update_handler,
        )

    def on(self, event: str, listener: Callable):
        self._emitter.on(event, listener)

    def is_closed(self) -> bool:
        """

        Returns
        -------
        bool
            True if closed, otherwise False
        """
        return self._closed is True

    def is_authorized(self) -> bool:
        """

        Returns
        -------
        bool
            True if authorized, otherwise False
        """
        if self.is_closed():
            return False

        return self._authorized

    async def authorize(self) -> bool:
        """
        The method starts process authorization

        Returns
        -------
        bool
            True if authorized, otherwise False
        """
        if self.is_authorized():
            return True

        self.debug("AuthManager: start authorize")
        authorization = asyncio.create_task(self._do_authorize())
        result = await authorization
        self.debug(f"AuthManager: end authorize, result {result}")
        return result

    async def _do_authorize(self):
        self.debug("AuthManager: do authorize")

        if self.is_authorized():
            return True

        self._closed = False
        self._authorized = False
        self._daemon = Daemon(DEFAULT_EXPIRES_IN_SEC)
        self._daemon.start()

        self.debug(
            f"AuthManager: Access token will be requested "
            f"in {self._access_token_updater.delay} seconds"
        )
        authorization = asyncio.create_task(self._access_token_updater.start())
        authorization.add_done_callback(handle_exception)
        await authorization

        if self._authorized:
            latency_secs = self._access_token_updater.latency_secs
            delay = self._token_info.get().calc_expires_in(latency_secs)
            self._refresh_token_updater.delay = delay
            self.debug(
                f"AuthManager: Refresh token will be requested "
                f"in {self._refresh_token_updater.delay} seconds"
            )
            task = asyncio.create_task(self._refresh_token_updater.start())
            task.add_done_callback(handle_exception)

        return self._authorized

    def close(self):
        """
        The method stops refresh token updater and access token updater

        Returns
        -------
        None
        """
        self.debug("AuthManager: close")
        if self.is_closed():
            return

        self._daemon and self._daemon.cancel()
        self._access_token_updater.stop()
        self._refresh_token_updater.stop()
        self._authorized = False
        self._closed = True

    async def _access_token_update_handler(
        self, event: str, message: str, json_content: dict
    ) -> None:
        self.debug(
            f"AuthManager: Access token handler, event: {event}, message: {message}"
        )

        if event is UpdateEvent.ACCESS_TOKEN_SUCCESS:
            self._authorized = True
            delays.reset()
            token_info = create_token_info(json_content)
            self._token_info.set(token_info)
            access_token = token_info.access_token
            self.debug(
                f"Access token {access_token}. "
                f"Expire in {token_info.expires_in} seconds"
            )
            self._emitter.emit(UpdateEvent.UPDATE_ACCESS_TOKEN, access_token)
            self._access_token_updater.stop()
            self._emitter.emit(event, message)
            self._emitter.emit(UpdateEvent.AUTHENTICATION_SUCCESS, message)

        elif event is UpdateEvent.ACCESS_TOKEN_UNAUTHORIZED:
            self._authorized = False
            self._access_token_updater.stop()
            self._emitter.emit(event, message)
            self._emitter.emit(UpdateEvent.AUTHENTICATION_FAILED, message)
            self.close()
            self._emitter.emit(UpdateEvent.CLOSE_SESSION)

        elif event is UpdateEvent.ACCESS_TOKEN_FAILED:
            if not self._auto_reconnect:
                self._authorized = False
                self._access_token_updater.stop()

            self._emitter.emit(event, message)
            self._emitter.emit(UpdateEvent.AUTHENTICATION_FAILED, message)

            if self._auto_reconnect:
                delay = delays.next()
                self.debug(f"AuthManager: reconnecting in {delay} secs")
                self._access_token_updater.delay = delay
                self._emitter.emit(UpdateEvent.RECONNECTING, message)

            else:
                self.close()
                self._emitter.emit(UpdateEvent.CLOSE_SESSION)

        await asyncio.sleep(0)

    async def _refresh_token_update_handler(
        self, event: str, message: str, json_content: dict
    ) -> None:
        self.debug(
            f"AuthManager: Refresh token handler, event: {event}, message: {message}"
        )

        if event is UpdateEvent.REFRESH_TOKEN_SUCCESS:
            token_info = create_token_info(json_content)
            self._token_info.set(token_info)
            access_token = token_info.access_token
            self.debug(
                f"Received access token {token_info.refresh_token}. "
                f"Expire in {token_info.expires_in} seconds"
            )
            self._emitter.emit(UpdateEvent.UPDATE_ACCESS_TOKEN, access_token)
            latency_secs = self._access_token_updater.latency_secs
            delay = token_info.calc_expires_in(latency_secs)
            self._refresh_token_updater.delay = delay
            self.debug(f"Set refresh token delay to {delay} seconds")
            self._emitter.emit(event, message)

        elif event is UpdateEvent.REFRESH_TOKEN_BAD:
            self._authorized = False
            self._emitter.emit(event, message)
            self._emitter.emit(UpdateEvent.AUTHENTICATION_FAILED, message)
            self.close()
            self._emitter.emit(UpdateEvent.CLOSE_SESSION)

        elif event is UpdateEvent.REFRESH_TOKEN_FAILED:
            self._emitter.emit(event, message)
            self._emitter.emit(UpdateEvent.AUTHENTICATION_FAILED, message)

            if self._auto_reconnect:
                delay = delays.next()
                self.debug(
                    f"AuthManager: Trying to get Refresh token again in {delay} secs"
                )
                self._refresh_token_updater.delay = delay
                self._emitter.emit(UpdateEvent.RECONNECTING, message)

            else:
                self._authorized = False
                self.close()
                self._emitter.emit(UpdateEvent.CLOSE_SESSION)

        elif event is UpdateEvent.REFRESH_TOKEN_EXPIRED:
            self._emitter.emit(event, message)
            self._emitter.emit(UpdateEvent.AUTHENTICATION_FAILED, message)

            if self._auto_reconnect:
                self.debug("AuthManager: reconnecting")
                self._emitter.emit(UpdateEvent.RECONNECTING, message)
                self.close()
                asyncio.create_task(self._do_authorize())

            else:
                self._authorized = False
                self.close()
                self._emitter.emit(UpdateEvent.CLOSE_SESSION)

        await asyncio.sleep(0)

    def dispose(self):
        """
        The method destroy an instance

        Returns
        -------
        None
        """
        self.close()
        self._access_token_updater.dispose()
        self._refresh_token_updater.dispose()
        self._authorized = None
        self._session = None
