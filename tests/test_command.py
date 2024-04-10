import re

from triton_testcontainer.command import TritonCommand

def test_command_correct():
    cmd = TritonCommand(
        id="test",
        exit_timeout_secs=10,
        log_verbose=6,
        log_info=True,
        log_warning=True,
        log_error=True,
        model_store=["/workspace/models"],
        model_repository=["/workspace", "/home"], 
        exit_on_error=True,
        disable_auto_complete_config=True,
        strict_readiness=True,
        model_control_mode="explicit", 
        load_model=["simple", "hard"],
        model_load_thread_count=5,
        model_load_retry_count=4,
        model_namespacing=True,
        allow_metrics=True,
    ).build()

    assert cmd.startswith("tritonserver")

    options = [
        "--id=test",
        "--exit-timeout-secs=10",
        "--log-verbose=6",
        "--log-info=1",
        "--log-warning=1",
        "--log-error=1",
        "--model-store=/workspace/models",
        "--model-repository=/workspace",
        "--model-repository=/home",
        "--exit-on-error=1",
        "--disable-auto-complete-config",
        "--strict-readiness=1",
        "--model-control-mode=explicit",
        "--load-model=simple",
        "--load-model=hard",
        "--model-load-thread-count=5",
        "--model-load-retry-count=4",
        "--model-namespacing=1",
        "--allow-metrics=1",
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
    

