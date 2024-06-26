from typing import TypedDict, Literal
from typing_extensions import NotRequired

import docker.types
import geventhttpclient

import tritonclient.http as tritonhttpclient

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

from .command import TritonCommand

TRITON_HTTP_PORT = 8000
TRITON_GRPC_PORT = 8001
TRITON_METRICS_PORT = 8002
DEFAULT_TRITON_CONTAINER_COMMAND = TritonCommand(
    model_repository=["/home"],
    model_control_mode="explicit",
).build()


class VolumeMapping(TypedDict):
    host: str
    container: str
    mode: NotRequired[str]


class TritonContainer(DockerContainer):
    """
    Triton Container
    """

    def __init__(
            self,
            repository: str = "nvcr.io/nvidia/tritonserver",
            tag: str = "24.01-py3",
            name: str = "tritonserver",
            with_gpus: bool = True,
            volume_mapping: list[VolumeMapping] | None = None,
            command: str = DEFAULT_TRITON_CONTAINER_COMMAND,
            **kwargs
    ) -> None:
        image = f"{repository}:{tag}"

        super().__init__(image, **kwargs)
        self.with_exposed_ports(TRITON_HTTP_PORT, TRITON_GRPC_PORT, TRITON_METRICS_PORT)
        self.with_command(command)
        self.with_name(name)

        if volume_mapping:
            for mapping in volume_mapping:
                self.with_volume_mapping(
                    host=mapping["host"],
                    container=mapping["container"],
                    mode=mapping.get("mode", "ro")
                )

        if with_gpus:
            self.with_kwargs(
                device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])]
            )

    def get_url(self, port_name: Literal["http"] | Literal["grpc"] | Literal["metrics"] = "http") -> str:

        match port_name:
            case "http":
                port = TRITON_HTTP_PORT
            case "grpc":
                port = TRITON_GRPC_PORT
            case "metrics":
                port = TRITON_METRICS_PORT
            case _:
                raise ValueError(f"Unknown port name {port_name}")

        return f"{self.get_container_host_ip()}:{self.get_exposed_port(port)}"

    def get_client(self) -> tritonhttpclient.InferenceServerClient:

        triton_host = self.get_container_host_ip()
        triton_http_port = self.get_exposed_port(TRITON_HTTP_PORT)

        triton_url = f"{triton_host}:{triton_http_port}"

        return tritonhttpclient.InferenceServerClient(
            url=triton_url,
            verbose=False,
        )

    @wait_container_is_ready(tritonhttpclient.InferenceServerException,
                             geventhttpclient.response.HTTPConnectionClosed)
    def readiness_probe(self):
        triton_client = self.get_client()
        if not triton_client.is_server_ready():
            raise tritonhttpclient.InferenceServerException("Server not ready yet.")

    def start(self) -> "TritonContainer":
        super().start()
        self.readiness_probe()
        return self
