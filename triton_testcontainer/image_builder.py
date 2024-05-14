from typing import Optional, Iterator, IO, Any, TypedDict
import io
import functools

from dataclasses import dataclass, asdict, field
from docker.models.images import ImageCollection, Image
from testcontainers.core.docker_client import DockerClient


class ContainerLimits(TypedDict):
    memory: int
    memswap: int
    cpushares: int
    cpusetcpus: str


@dataclass
class BuildOptions:
    quiet: bool = False
    nocache: bool = False
    rm: bool = False
    timeout: int = 30
    custom_context: bool = False
    encoding: str = "gzip"
    pull: bool = False
    forcerm: bool = False
    buildargs: dict = field(default_factory=dict)
    container_limits: ContainerLimits = field(default_factory=dict)
    shmsize: int = 67_108_864,  # 64MB
    labels: dict = field(default_factory=dict)
    cache_from: list = field(default_factory=list)
    target: str = ""
    network_mode: str = "host"
    squash: bool = False
    extra_hosts: dict = field(default_factory=dict)
    platform: str = ""
    isolation: str | None = None
    use_config_proxy: bool = False


class ImageBuilder:
    def __init__(
            self,
            docker_client_kw: Optional[dict] = None,
            tag: str = "localhost/image_builder:latest",
    ):
        self._docker = DockerClient(**(docker_client_kw or {}))
        self.tag = tag

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def from_path(
            self, context: str, path_to_dockerfile: str, options: BuildOptions = BuildOptions(), **kwargs: Optional[Any]
    ) -> tuple[Image, Optional[Iterator]]:
        results = self.build(path=context, dockerfile=path_to_dockerfile, build_options=options, **kwargs)
        return results

    def from_string(
            self, context: str, string_dockerfile: str, options: BuildOptions = BuildOptions(), **kwargs: Optional[Any]
    ) -> tuple[Image, Optional[Iterator]]:
        file_obj = io.BytesIO(bytes(string_dockerfile, encoding='utf-8'))
        return self.build(path=context, fileobj=file_obj, build_options=options, **kwargs)

    @functools.wraps(ImageCollection.build)
    def build(
            self,
            path: str | None = None,
            fileobj: IO | None = None,
            dockerfile: str = "",
            build_options: BuildOptions = BuildOptions(),
            **kwargs: Optional[Any]
    ) -> tuple[Image, Optional[Iterator]]:
        all_options = {**asdict(build_options), **kwargs}

        docker_client = self.get_docker_client()

        result = docker_client.client.images.build(
            path=path,
            fileobj=fileobj,
            dockerfile=dockerfile,
            tag=self.tag,
            **all_options
        )

        if isinstance(result, Image):
            return result, None

        return result
