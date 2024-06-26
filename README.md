# Triton Testcontainer

This package started as an implementation of testcontainer module for Nvidi Triton, but also added other functionality that extends beyond simply running containers withing pytest.

## Usage

This package provides several functions:
* triton container (class `TritonContainer`): manage tritonserver container within a testsuite.

* dockerfile builder (class `DockerfileBuilder`): Dockerfile DSL for generating dockerfiles programatically.

* docker image builder (class `ImageBuilder`): Builing images on fly, e.g. within a testsuite.

## Installation

```bash
pip3 install git+https://github.com/ogvalt/triton-testcontainer.git@v0.6.1
```
    
## Examples

```python
import pytest
import triton_testcontainer as tritoncontainer


@pytest.fixture(scope="session") # Specify scope of fixture
def setup_triton(request):
    # start triton
    triton = tritoncontainer.TritonContainer() # Create container instance

    triton.start() # launches container, waits until it's ready

    def remove_triton_container(): 
        triton.stop() # stops container

    request.addfinalizer(remove_triton_container) # handles container at the end of testing session

    return triton.get_client() # returns triton http client 

def test_example(setup_triton):
    triton_client: 'tritonclient.http.InferenceServerClient' = setup_triton
    assert True

def test_example_two():
    cmd = tritoncontainer.TritonCommand(model_repository=["/models"]).build() # command to run tritonserver with

    maps = [{"host": "/path/to/repository", "container": "/models"}] # map repository on host to container

    # use context manager to run container on __enter__ and stop it on __exit__
    with tritoncontainer.TritonContainer(with_gpus=True, volume_mapping=maps, command=cmd) as service:  
        triton_client = service.get_client()
        assert True     
```

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from triton_testcontainer import ImageBuilder, DockerfileBuilder


def test_example_three():
    dockerfile = (DockerfileBuilder() \
                  .from_("ubuntu:20.04") \
                  .cmd("echo", "hello world")
                  .build())


    with ImageBuilder("hello-world").from_string(context=".", string_dockerfile=dockerfile).ctx_manager() as image:
        with DockerContainer(image.tags[0]) as container:
            delay = wait_for_logs(container, "hello world", 30)