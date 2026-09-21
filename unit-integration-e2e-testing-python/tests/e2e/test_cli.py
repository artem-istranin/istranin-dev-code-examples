import shutil
import subprocess

import pytest


@pytest.mark.acceptance
def test_weather_conversion_from_terminal(tmp_path):
    command = shutil.which("units-convert")
    assert command is not None, "Install the project with uv sync --locked"

    result = subprocess.run(
        [command, "25", "C", "F"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "77"
    assert result.stderr == ""


@pytest.mark.parametrize(
    "source, target, message",
    [
        ("m", "kg", "different dimensions"),
        ("unknown", "m", "Unknown unit: unknown"),
        ("m", "unknown", "Unknown unit: unknown"),
    ],
)
def test_invalid_conversion_reports_failure(tmp_path, source, target, message):
    command = shutil.which("units-convert")
    assert command is not None, "Install the project with uv sync --locked"

    result = subprocess.run(
        [command, "1", source, target],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert message in result.stderr
