from typing import Optional, Iterator, TextIO, Any, TypedDict
import functools

from docker.models.images import ImageCollection, Image

from testcontainers.core.docker_client import DockerClient

class ContainerLimits(TypedDict):
    memory: int
    memswap: int
    cpushares: int
    cpusetcpus: str


class ImageBuilder:
    def __init__(
            self,
            docker_client_kw: Optional[dict] = None,
        ):
        self._docker = DockerClient(**(docker_client_kw or {}))

    def from_path(self, context: str, path_to_dockerfile: str):
        ...

    def from_string(self, context: str, string_dockerfile: str):
        ...

    def get_docker_client(self) -> DockerClient:
        return self._docker
    
    @functools.wraps(ImageCollection.build)
    def build(
            self,
            path: str,
            fileobj: TextIO,
            dockerfile: str = ...,
            tag: str = "localhost/image_builder:latest",
            quite: bool = False,
            nocache: bool = False,
            rm: bool = False,
            timeout: int = 30,
            custom_context: bool = False,
            encoding: str = "gzip",
            pull: bool = False,
            forcerm: bool = False,            
            buildargs: dict | None = None,
            container_limits: ContainerLimits | None = None,
            shmsize: int = 67_108_864, # 64MB
            labels: dict | None = None,
            cache_from: list | None = None,
            target: str = "",
            network_mode: str = "host",
            squash: bool = False,
            extra_hosts: dict | None = None,
            platform: str = "",
            isolation: str | None = None,
            use_config_proxy: bool = False,
            **kwargs: Optional[Any]
        ) -> tuple[Image, Optional[Iterator]]:
        if buildargs is None:
            buildargs = {}

        if container_limits is None:
            container_limits = {}

        if labels is None:
            labels = {}

        if cache_from is None:
            cache_from = []

        if extra_hosts is None:
            extra_hosts = {}

        docker_client = self.get_docker_client()
        result = docker_client.client.images.build(
            path=path,
            fileobj=fileobj,
            dockerfile=dockerfile,
            tag=tag,
            quiet=quite,
            nocache=nocache,
            rm=rm,
            timeout=timeout,
            custom_context=custom_context,
            encoding=encoding,
            pull=pull,
            forcerm=forcerm,
            buildargs=buildargs,
            container_limits=container_limits,
            shmsize=shmsize,
            labels=labels,
            cache_from=cache_from,
            target=target,
            network_mode=network_mode,
            squash=squash,
            extra_hosts=extra_hosts,
            platform=platform,
            isolation=isolation,
            use_config_proxy=use_config_proxy,
            **kwargs
        )

        return result