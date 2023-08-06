import abc
import collections
import json
import pathlib
from typing import List
from typing import TYPE_CHECKING
from typing import Union

from .proxy_info import ProxyInfo
from ...configure import keys
from ...core.session._session_cxn_type import SessionCxnType
from ...tools import urljoin, parse_url

if TYPE_CHECKING:
    from ...core.session import Session, PlatformSession
    from ...configure import _RDPConfig

StreamServiceInfo = collections.namedtuple(
    "StreamServiceInfo",
    ["scheme", "host", "port", "path", "data_formats", "location"],
)

_DEFAULT_RECONNECTION_DELAY_SECS = 5


class StreamCxnConfig(abc.ABC):
    def __init__(
        self,
        infos: Union[List["StreamServiceInfo"], "StreamServiceInfo"],
        protocols: Union[List[str], str],
    ):
        if isinstance(infos, list) and len(infos) == 0:
            raise ValueError("infos are empty")

        if not isinstance(infos, list):
            infos = [infos]

        if not isinstance(protocols, list):
            protocols = [protocols]

        self._infos = infos
        self._protocols = protocols
        self._index = 0

    @property
    def info(self):
        return self._infos[self._index]

    @property
    def url(self):
        return self._get_url(self.info)

    @property
    def url_scheme(self):
        return self.info.scheme

    @property
    def urls(self):
        return [self._get_url(info) for info in self._infos]

    @property
    def headers(self):
        return []

    @property
    def data_formats(self):
        return self.info.data_formats

    @property
    def supported_protocols(self):
        return self._protocols

    def reset_reconnection_config(self):
        self._index = 0

    @property
    def no_proxy(self):
        return ProxyInfo.get_no_proxy()

    @property
    def proxy_config(self):
        proxies_info = ProxyInfo.get_proxies_info()
        if self.url_scheme == "wss":
            # try to get https proxy then http proxy if https not configured
            return proxies_info.get("https", proxies_info.get("http", None))
        else:
            return proxies_info.get("http", None)

    @property
    def data_fmt(self):
        if not self.data_formats:
            return ""
        return self.data_formats[0]

    @property
    def delay(self):
        return self._index * _DEFAULT_RECONNECTION_DELAY_SECS

    def set_next_url(self):
        self._index = (self._index + 1) % len(self._infos)

    @abc.abstractmethod
    def _get_url(self, info: "StreamServiceInfo") -> str:
        pass

    def __str__(self) -> str:
        urls = "\n\t\t\t ".join(self.urls)
        s = (
            f"{self.__class__.__name__} {{\n"
            f"\t\tinfo={self.info},\n"
            f"\t\turl={self.url},\n"
            f"\t\turl_scheme={self.url_scheme},\n"
            f"\t\turls={urls},\n"
            f"\t\theaders={self.headers}, "
            f"data_formats={self.data_formats}, "
            f"supported_protocols={self.supported_protocols}, "
            f"no_proxy={self.no_proxy}, "
            f"proxy_config={self.proxy_config}, "
            f"data_fmt={self.data_fmt}, "
            f"delay={self.delay}}}"
        )
        return s


class DesktopStreamCxnConfig(StreamCxnConfig):
    def __init__(
        self,
        session: "Session",
        infos: Union[List["StreamServiceInfo"], "StreamServiceInfo"],
        protocols: Union[List[str], str],
    ):
        super().__init__(infos, protocols)
        self._session = session

    @property
    def headers(self):
        if self._session._access_token:
            return [
                f"x-tr-applicationid: {self._session.app_key}",
                f"Authorization: Bearer {self._session._access_token}",
            ]

        else:
            return [f"x-tr-applicationid: {self._session.app_key}"]

    def _get_url(self, info: "StreamServiceInfo") -> str:
        return f"{info.scheme}://{info.host}:{info.port}/{info.path}"


class PlatformStreamCxnConfig(StreamCxnConfig):
    def _get_url(self, info: "StreamServiceInfo") -> str:
        path = info.path or "WebSocket"
        return f"{info.scheme}://{info.host}:{info.port}/{path}"


class NullStreamCxnConfig(StreamCxnConfig):
    def __init__(self):
        StreamCxnConfig.__init__(self, [StreamServiceInfo("", "", "", "", "", "")], [])

    def _get_url(self, info):
        return ""


def get_discovery_url(
    root_url: str, streaming_name: str, endpoint_name: str, config: "_RDPConfig"
) -> str:
    config_name = f"apis.streaming.{streaming_name}"
    config_endpoint_name = f"{config_name}.endpoints.{endpoint_name}"
    base_path = config.get_str(f"{config_name}.url")

    try:
        endpoint_path = config.get_str(f"{config_endpoint_name}.path")
    except KeyError:
        raise KeyError(
            f"Cannot find discovery endpoint '{endpoint_name}' "
            f"for streaming '{streaming_name}' in config."
        )

    url = urljoin(root_url, base_path)
    url = urljoin(url, endpoint_path)
    return url


def _filter_by_location(locations: List[str], infos: List[StreamServiceInfo]) -> list:
    if not locations:
        return infos

    filtered = []
    for location in locations:
        for info in infos:
            has_location = any(
                loc.strip().startswith(location) for loc in info.location
            )
            if has_location:
                filtered.append(info)

    return filtered


class CxnConfigProvider(abc.ABC):
    config_class = None

    async def get_cfg_async(
        self, session: "Session", api_cfg_key: str
    ) -> Union[PlatformStreamCxnConfig, DesktopStreamCxnConfig]:
        """
        Parameters
        ----------
        session: Session
        api_cfg_key: str
            Example - "streaming/pricing/main"

        Returns
        -------
        PlatformStreamCxnConfig or DesktopStreamCxnConfig

        """
        _, content_name, endpoint_name = api_cfg_key.split("/")
        cfg: "_RDPConfig" = session.config

        websocket_url: str = cfg.get(
            keys.get_stream_websocket_url(content_name, endpoint_name)
        )

        if websocket_url is not None:
            result = parse_url(websocket_url)

            path = result.path
            host = result.hostname

            if not result.hostname and result.path:
                path = ""
                host = result.path

            scheme = result.scheme
            port = result.port

            if not scheme and port == 443:
                scheme = "wss"

            if not scheme and port == 80:
                scheme = "ws"

            info = StreamServiceInfo(
                scheme=scheme or "ws",
                host=host or "",
                port=port or 80,
                path=path or "",
                data_formats=["unknown"],
                location="",
            )
            infos = [info]

        else:
            url_root: str = session._get_rdp_url_root()
            discovery_url: str = get_discovery_url(
                url_root, content_name, endpoint_name, cfg
            )
            infos = await self._request_infos(discovery_url, api_cfg_key, cfg, session)

        protocols = cfg.get_list(keys.stream_protocols(content_name, endpoint_name))
        cxn_config = self._create_cfg(session, infos, protocols)
        return cxn_config

    async def _request_infos(
        self,
        discovery_url: str,
        api_config_key: str,
        config: "_RDPConfig",
        session: "Session",
    ) -> List[StreamServiceInfo]:
        response = await session.http_request_async(discovery_url)
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            raise RuntimeError(f"Cannot load config from {discovery_url}, {response}")

        services = data.get("services", [])

        infos = []
        for service in services:
            if service.get("transport") == "websocket":
                endpoint = service.get("endpoint")
                port = service.get("port")
                data_format = service.get("dataFormat")
                location = service.get("location")

                endpoint_path = pathlib.Path(endpoint)

                host = str(endpoint_path.parts[0])
                if len(endpoint_path.parts) > 1:
                    path = "/".join(endpoint_path.parts[1:])

                else:
                    path = None

                scheme = "ws"
                if port == 443:
                    scheme = "wss"

                if port == 80:
                    scheme = "ws"

                info = StreamServiceInfo(
                    scheme=scheme or "",
                    host=host or "",
                    port=port or "",
                    path=path or "",
                    data_formats=data_format or ["unknown"],
                    location=location or "",
                )
                infos.append(info)

        infos = self._filter_infos(infos, api_config_key, config)
        return infos

    def _filter_infos(
        self,
        infos: List[StreamServiceInfo],
        api_cfg_key: str,
        cfg: "_RDPConfig",
    ) -> List[StreamServiceInfo]:
        return infos

    def _create_cfg(
        self, session: "Session", infos: List[StreamServiceInfo], protocols: List[str]
    ) -> Union[PlatformStreamCxnConfig, DesktopStreamCxnConfig]:
        cxn_config = self.config_class(infos, protocols)
        return cxn_config


class DesktopCxnConfigProvider(CxnConfigProvider):
    config_class = DesktopStreamCxnConfig

    def _create_cfg(
        self, session: "Session", infos: List[StreamServiceInfo], protocols: List[str]
    ) -> Union[PlatformStreamCxnConfig, DesktopStreamCxnConfig]:
        cxn_config = self.config_class(session, infos, protocols)
        return cxn_config


class PlatformCxnConfigProvider(CxnConfigProvider):
    config_class = PlatformStreamCxnConfig

    def _filter_infos(
        self,
        infos: List[StreamServiceInfo],
        api_cfg_key: str,
        cfg: "_RDPConfig",
    ) -> List[StreamServiceInfo]:
        _, content_name, endpoint_name = api_cfg_key.split("/")

        locations = cfg.get_list(
            keys.stream_connects_locations(content_name, endpoint_name)
        )
        infos = _filter_by_location(locations, infos)
        return infos


class DeployedCxnConfigProvider(CxnConfigProvider):
    async def get_cfg_async(
        self, session: "PlatformSession", api_cfg_key: str
    ) -> PlatformStreamCxnConfig:

        deployed_host: str = session._deployed_platform_host

        if deployed_host is not None:
            url = deployed_host

        else:
            session_name: str = session.name
            config: "_RDPConfig" = session.config
            key = keys.platform_realtime_distribution_system(session_name)
            url_key = f"{key}.url"
            url = config.get_str(url_key)

        result = parse_url(url)
        scheme = result.scheme

        if "." in scheme:
            host = scheme
            port = result.path
            try:
                port = int(port)
            except ValueError:
                port = ""

            scheme = ""

        else:
            host = result.hostname or result.netloc or result.path
            port = result.port

        if not scheme and port == 443:
            scheme = "wss"

        if not scheme and port == 80:
            scheme = "ws"

        info = StreamServiceInfo(
            scheme=scheme or "ws",
            host=host or "",
            port=port or 80,
            path="",
            data_formats=["tr_json2"],
            location="",
        )

        cxn_config = PlatformStreamCxnConfig(info, "OMM")
        return cxn_config


class PlatformAndDeployedCxnConfigProvider(
    DeployedCxnConfigProvider, PlatformCxnConfigProvider
):
    scheme: str = "ws"

    async def get_cfg_async(
        self, session: "PlatformSession", api_cfg_key: str
    ) -> StreamCxnConfig:

        if api_cfg_key.startswith("streaming/pricing/main"):
            cxn_config = await DeployedCxnConfigProvider.get_cfg_async(
                self, session, api_cfg_key
            )

        else:
            cxn_config = await PlatformCxnConfigProvider.get_cfg_async(
                self, session, api_cfg_key
            )

        return cxn_config


cxn_cfg_provider_by_session_cxn_type = {
    SessionCxnType.DEPLOYED: DeployedCxnConfigProvider(),
    SessionCxnType.REFINITIV_DATA: PlatformCxnConfigProvider(),
    SessionCxnType.REFINITIV_DATA_AND_DEPLOYED: PlatformAndDeployedCxnConfigProvider(),
    SessionCxnType.DESKTOP: DesktopCxnConfigProvider(),
}


async def get_cxn_config_async(
    api_config_key: str, session: "Session"
) -> StreamCxnConfig:
    session_cxn_type = session._get_session_cxn_type()
    cxn_cfg_provider = cxn_cfg_provider_by_session_cxn_type.get(session_cxn_type)

    if not cxn_cfg_provider:
        raise ValueError(
            f"Can't find cxn_cfg_provider by session_cxn_type={session_cxn_type}"
        )

    cfg = await cxn_cfg_provider.get_cfg_async(session, api_config_key)
    return cfg
