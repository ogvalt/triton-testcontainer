import pathlib

import tritonclient.http as tritonhttpclient
import numpy as np

from triton_testcontainer import TritonContainer
from triton_testcontainer.command import TritonCommand


def test_triton_container(datadir: pathlib.Path):

    host_model_repository = datadir / "models_repository"
    example_model_repository = "/models"
    model_name = "simple"

    cmd = TritonCommand(
        model_repository=[example_model_repository],
        model_control_mode="explicit",
        load_model=model_name,
    ).build()

    volume_mapping = [
        {
            "host": host_model_repository,
            "container": example_model_repository
        },
    ]

    with TritonContainer(
        with_gpus=False, 
        volume_mapping=volume_mapping, 
        command=cmd
        ) as triton:

        triton_client = triton.get_client()
        
        inputs = []
        outputs = []
        inputs.append(tritonhttpclient.InferInput("INPUT0", [8, 16], "INT32"))
        inputs.append(tritonhttpclient.InferInput("INPUT1", [8, 16], "INT32"))

        # Initialize the data
        inputs[0].set_data_from_numpy(np.ones([8, 16], dtype=np.int32))
        inputs[1].set_data_from_numpy(np.zeros([8, 16], dtype=np.int32))

        outputs.append(tritonhttpclient.InferRequestedOutput("OUTPUT0"))
        outputs.append(tritonhttpclient.InferRequestedOutput("OUTPUT1"))

        results = triton_client.infer(
            model_name,
            inputs,
            model_version="1",
            outputs=outputs,
            )

        output0_data = results.as_numpy("OUTPUT0")
        output1_data = results.as_numpy("OUTPUT1")

        assert triton_client.is_model_ready(model_name, model_version="1")
        np.testing.assert_array_equal(output0_data, np.ones([8, 16], dtype=np.int32))
        np.testing.assert_array_equal(output1_data, np.ones([8, 16], dtype=np.int32))