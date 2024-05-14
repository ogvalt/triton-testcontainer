from typing import Optional, Any, TypedDict
import io
import functools
from contextlib import contextmanager

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
    """

    Example:
        with ImageBuilder().from_string().ctx_manager() as image:
            print(image.tags)
    """

    def __init__(
            self,
            docker_client_kw: Optional[dict] = None,
            tag: str = "localhost/image_builder:latest",
            reuse: bool = False,
            **kwargs: dict
    ):
        self._docker = DockerClient(**(docker_client_kw or {}))
        self._image = None
        self._context = None
        self._dockerfile_path = None
        self._string_dockerfile = None
        self._build_options = None
        self._build_kwargs = None
        self._build_log = None

        self._kwargs = kwargs

        self.tag = tag
        self.reuse = reuse

    @property
    def image(self) -> Image:
        return self._image

    def get_docker_client(self) -> DockerClient:
        return self._docker

    def from_path(
            self, context: str, path_to_dockerfile: str, options: BuildOptions = BuildOptions(), **kwargs: Optional[Any]
    ) -> 'ImageBuilder':
        self._context = context
        self._dockerfile_path = path_to_dockerfile
        self._build_options = options
        self._build_kwargs = kwargs
        return self

    def from_string(
            self, context: str, string_dockerfile: str, options: BuildOptions = BuildOptions(), **kwargs: Optional[Any]
    ) -> 'ImageBuilder':
        self._context = context
        self._string_dockerfile = io.BytesIO(bytes(string_dockerfile, encoding='utf-8'))
        self._build_options = options
        self._build_kwargs = kwargs
        return self

    @functools.wraps(ImageCollection.build)
    def build(self) -> Image:
        all_options = {**asdict(self._build_options), **self._build_kwargs}

        docker_client = self.get_docker_client()

        result = docker_client.client.images.build(
            path=self._context,
            fileobj=self._string_dockerfile,
            dockerfile=self._dockerfile_path,
            tag=self.tag,
            **all_options
        )

        if isinstance(result, Image):
            self._image, self._build_log = result, None

        self._image, self._build_log = result

        return self.image

    @functools.wraps(Image.remove)
    def remove(self):
        force = False
        if "force" in self._kwargs:
            force = self._kwargs.get("force")

        no_prune = False
        if "noprune" in self._kwargs:
            no_prune = self._kwargs.get("noprune")
        return self._image.remove(force, no_prune)

    @contextmanager
    def ctx_manager(self):
        try:
            yield self.build()
        finally:
            self.remove()
