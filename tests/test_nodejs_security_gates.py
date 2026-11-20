"""Tests for the nodejs-security-audit gates, run the way squad runs them.

squad runs each gate command with bash from the audited project's root and
stops the pipeline on the first non-zero exit. These tests load the commands
from agent.yaml and run them against throwaway project layouts.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

AGENT_YAML = Path(__file__).parent.parent / "nodejs-security-audit" / "agent.yaml"
BASH = shutil.which("bash")
STAGES = ["injection", "resources"]

pytestmark = pytest.mark.skipif(
    BASH is None or shutil.which("npm") is None,
    reason="the gates need bash and npm on PATH",
)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    return root


def write_package(project: Path, scripts: dict[str, str] | None = None) -> None:
    manifest = {"name": "fixture", "version": "1.0.0", "scripts": scripts or {}}
    (project / "package.json").write_text(json.dumps(manifest))


def add_tool(project: Path, name: str, exit_code: int = 0) -> Path:
    """Install a stand-in for a project-local CLI; return the file it logs its arguments to."""
    log = project / f"{name}.args"
    tool = project / "node_modules" / ".bin" / name
    tool.parent.mkdir(parents=True, exist_ok=True)
    tool.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{log}"\nexit {exit_code}\n')
    tool.chmod(0o755)
    return log


def gates_pass(project: Path, stage: str) -> bool:
    """Run every gate configured after `stage`, stopping at the first failure."""
    gates = yaml.safe_load(AGENT_YAML.read_text(encoding="utf-8"))["gates"]
    commands = [gate["command"] for gate in gates if gate["after"] == stage]
    assert commands, f"no gates run after {stage}"
    env = {
        **os.environ,
        "npm_config_cache": str(project.parent / "npm-cache"),
        "npm_config_offline": "true",
        "npm_config_update_notifier": "false",
    }
    for command in commands:
        gate = subprocess.run(  # noqa: S603
            [BASH, "-c", command], cwd=project, env=env, capture_output=True
        )
        if gate.returncode != 0:
            return False
    return True


@pytest.mark.parametrize("stage", STAGES)
def test_gates_skip_without_root_package_json(project, stage):
    (project / "tsconfig.json").write_text("{}")
    assert gates_pass(project, stage)


@pytest.mark.parametrize("stage", STAGES)
def test_gates_pass_when_project_defines_no_checks(project, stage):
    write_package(project)
    assert gates_pass(project, stage)


@pytest.mark.parametrize("stage", STAGES)
def test_failing_build_fails_gate(project, stage):
    write_package(project, {"build": "exit 2"})
    assert not gates_pass(project, stage)


@pytest.mark.parametrize("stage", STAGES)
def test_type_check_runs_project_typescript(project, stage):
    write_package(project)
    (project / "tsconfig.json").write_text("{}")
    log = add_tool(project, "tsc")
    assert gates_pass(project, stage)
    assert log.read_text().split() == ["--noEmit"]


@pytest.mark.parametrize("stage", STAGES)
def test_type_error_fails_gate_without_build_script(project, stage):
    write_package(project)
    (project / "tsconfig.json").write_text("{}")
    add_tool(project, "tsc", exit_code=2)
    assert not gates_pass(project, stage)


@pytest.mark.parametrize("stage", STAGES)
def test_type_check_skipped_without_tsconfig(project, stage):
    write_package(project)
    log = add_tool(project, "tsc", exit_code=2)
    assert gates_pass(project, stage)
    assert not log.exists()


@pytest.mark.parametrize("stage", STAGES)
def test_type_check_fails_when_typescript_not_installed(project, stage):
    write_package(project)
    (project / "tsconfig.json").write_text("{}")
    assert not gates_pass(project, stage)


def test_npm_init_placeholder_test_script_passes(project):
    write_package(project, {"test": 'echo "Error: no test specified" && exit 1'})
    assert gates_pass(project, "resources")


def test_node_test_runner_passes(project):
    write_package(project, {"test": "node --test"})
    (project / "ok.test.js").write_text('require("node:test")("ok", () => {});\n')
    assert gates_pass(project, "resources")


def test_failing_tests_fail_gate(project):
    write_package(project, {"test": "node --test"})
    (project / "bad.test.js").write_text(
        'require("node:test")("bad", () => { throw new Error("boom"); });\n'
    )
    assert not gates_pass(project, "resources")


@pytest.mark.parametrize(
    ("script", "runner", "expected_args"),
    [
        ("jest", "jest", ["--passWithNoTests"]),
        ("vitest run", "vitest", ["run", "--passWithNoTests"]),
    ],
)
def test_jest_and_vitest_tolerate_no_tests(project, script, runner, expected_args):
    write_package(project, {"test": script})
    log = add_tool(project, runner)
    assert gates_pass(project, "resources")
    assert log.read_text().split() == expected_args


def test_failing_jest_fails_gate(project):
    write_package(project, {"test": "jest"})
    add_tool(project, "jest", exit_code=1)
    assert not gates_pass(project, "resources")


def test_no_tests_flag_stays_off_command_chained_after_jest(project):
    write_package(project, {"test": "jest && eslint ."})
    add_tool(project, "jest")
    log = add_tool(project, "eslint")
    assert gates_pass(project, "resources")
    assert log.read_text().split() == ["."]
