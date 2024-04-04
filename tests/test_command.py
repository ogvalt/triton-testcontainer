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
    

