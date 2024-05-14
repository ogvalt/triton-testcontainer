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

    with DockerContainer(image).with_name("pytest") as container:
        delay = wait_for_logs(container, predicate, timeout)

    assert True


def test_from_path(tmp_path):
    predicate = "ImageBuilder.from_path"
    dockerfile = (DockerfileBuilder() \
                  .from_("ubuntu:20.04") \
                  .cmd("echo", predicate)
                  .build())

    path_to_dockerfile = tmp_path / "Dockerfile"
    path_to_dockerfile.write_text(dockerfile)

    builder = ImageBuilder()

    image = builder.from_path(context=str(tmp_path), path_to_dockerfile=str(path_to_dockerfile)).build()

    assert_container_run(image.tags[0], predicate)

    builder.remove()


def test_from_string(tmp_path):
    predicate = "ImageBuilder.from_string"
    dockerfile = (DockerfileBuilder() \
                  .from_("ubuntu:20.04") \
                  .cmd("echo", predicate)
                  .build())

    builder = ImageBuilder()

    image = builder.from_string(context=str(tmp_path), string_dockerfile=dockerfile).build()

    assert_container_run(image.tags[0], predicate)

    builder.remove()


def test_context_manager(tmp_path):
    predicate = "ImageBuilder.from_string"
    dockerfile = (DockerfileBuilder() \
                  .from_("ubuntu:20.04") \
                  .cmd("echo", predicate)
                  .build())

    with (ImageBuilder(reuse=False).from_string(context=str(tmp_path), string_dockerfile=dockerfile).ctx_manager()) as image:
        assert_container_run(image.tags[0], predicate)
