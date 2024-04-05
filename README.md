# Triton Testcontainer

This is an implementation of testcontainers module for Nvidia Triton.

Package helps you use Docker containers for testing purposes.

# Installation

```bash
pip3 install git+https://github.com/ogvalt/triton-testcontainer.git@v0.1.0
```

# Usage

This package provides class `TritonContainer` that could be used as part of `pytest` `fixture` like in example below:

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
```
