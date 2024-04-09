import re

from triton_testcontainer.command import TritonCommand

def test_command_correct():
    cmd = TritonCommand(
        model_repository=["/workspace", "/home"], 
        model_control_mode="explicit", 
        load_model=["simple", "hard"],
    ).build()

    assert cmd.startswith("tritonserver")

    options = [
        "--model-repository=/workspace",
        "--model-repository=/home",
        "--model-control-mode=explicit",
        "--load-model=simple",
        "--load-model=hard",
    ]

    for substring in options:

        escaped_substring = re.escape(substring)
        pattern = rf"(?<= )({escaped_substring})(?= )|(?<= ){escaped_substring}$"

        assert len(re.findall(pattern=pattern, string=cmd)) == 1

def test_triton_command():
    cmd = TritonCommand(
        id="test",
        exit_timeout_secs=10,
        log_verbose=1,
        log_info=True,
        log_warning=True,
        log_error=True,
        model_store=["/workspace/models"],
        model_repository=["/workspace/models"],
        exit_on_error=True,
        disable_auto_complete_config=True,
        strict_readiness=True,
        model_control_mode="explicit",
        repository_pool_secs=10,
        load_model="test",
        model_load_thread_count=1,
        model_load_retry_count=1,
        model_namespacing=True,
        allow_metrics=True,
    )
    print(cmd.build())
    

