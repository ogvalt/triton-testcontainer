from triton_testcontainer.image_builder import ImageBuilder
from triton_testcontainer.dockerfile_builder import DockerfileBuilder


def assert_container_run(image: str, predicate: str, timeout: int = 30):
    """
    Idea behind this assert function is that we wait certain time until container is ready.
    If container is not ready within `timeout` error would be raised and test fails.
    If container is ready then `assert True`
    """
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.waiting_utils import wait_for_logs

    with DockerContainer(image) as container:
        delay = wait_for_logs(container, predicate, timeout)

    assert True


def test_from_path(tmp_path):
    predicate = "test ImageBuilder().from_path"

    dockerfile = (DockerfileBuilder() \
                  .from_("ubuntu:20.04") \
                  .cmd("echo", predicate)
                  .build())

    path_to_dockerfile = tmp_path / "Dockerfile"
    path_to_dockerfile.write_text(dockerfile)

    image, _ = ImageBuilder().from_path(context=str(tmp_path), path_to_dockerfile=str(path_to_dockerfile))

    assert_container_run(image.tags[0], predicate)


def test_from_string(tmp_path):
    predicate = "test ImageBuilder().from_string"

    dockerfile = (DockerfileBuilder() \
                  .from_("ubuntu:20.04") \
                  .cmd("echo", predicate)
                  .build())

    image, build_log = ImageBuilder().from_string(context=str(tmp_path), string_dockerfile=dockerfile)

    assert_container_run(image.tags[0], predicate)
