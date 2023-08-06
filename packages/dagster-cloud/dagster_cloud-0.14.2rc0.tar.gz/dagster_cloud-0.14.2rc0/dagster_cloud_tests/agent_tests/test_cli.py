# pylint: disable=unused-argument
import json
import os
import tempfile
from pathlib import Path

import mock
from dagster import Array, Field
from dagster.core.test_utils import environ
from dagster_cloud.agent.cli import app
from dagster_cloud.auth.constants import DEPLOYMENT_NAME_HEADER
from dagster_cloud.workspace.docker import DockerUserCodeLauncher
from typer.testing import CliRunner


def _check_dagster_home(expected: str):
    def _check_inner():
        assert os.getenv("DAGSTER_HOME") == expected

    return _check_inner


def test_run_command_with_env():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        with environ({"DAGSTER_HOME": temp_dir}):
            with mock.patch(
                "dagster_cloud.agent.cli.run_local_agent", _check_dagster_home(temp_dir)
            ):
                result = runner.invoke(app, [])

                assert result.exit_code == 0, result.output + " : " + str(result.exception)


def test_run_command_with_no_home():
    runner = CliRunner()

    with environ({"DAGSTER_HOME": None}):
        result = runner.invoke(app, [])

        assert result.exit_code == 1, result.output + " : " + str(result.exception)
        assert "No directory provided" in result.output


def test_run_command_with_argument():
    runner = CliRunner()

    # Test param works
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch(
            "dagster_cloud.agent.cli.run_local_agent",
            _check_dagster_home(str(Path(temp_dir).resolve())),
        ):
            result = runner.invoke(app, [temp_dir])

            assert result.exit_code == 0, result.output + " : " + str(result.exception)

    # Test param overrides DAGSTER_HOME env var
    with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as temp_dir_env:
        with environ({"DAGSTER_HOME": temp_dir_env}):
            with mock.patch(
                "dagster_cloud.agent.cli.run_local_agent",
                _check_dagster_home(str(Path(temp_dir).resolve())),
            ):
                result = runner.invoke(app, [temp_dir])

                assert result.exit_code == 0, result.output + " : " + str(result.exception)


TEST_TOKEN = "agent:hooli:1b2c814969d746b09d9k4d7e6g065cn4"


def test_run_ephemeral():
    runner = CliRunner()

    # Both directory and ephemeral config provided (error)
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, [temp_dir, "--agent-token", TEST_TOKEN, "--deployment", "prod"])

        assert result.exit_code == 1, result.output + " : " + str(result.exception)
        assert "Cannot supply both" in result.output

    # Missing part of ephemeral config (error)
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, ["--agent-token", TEST_TOKEN])

        assert result.exit_code == 1, result.output + " : " + str(result.exception)
        assert "both an agent token and a deployment" in result.output

    # Grab the DagsterCloudAgentInstance
    call_instance = [None]

    def mock_run_loop(_agent, instance, *args, **kwargs):
        call_instance[0] = instance

    # Minimal ephemeral config
    with mock.patch("dagster_cloud.agent.cli.DagsterCloudAgent.run_loop", mock_run_loop):
        result = runner.invoke(app, ["--agent-token", TEST_TOKEN, "--deployment", "staging"])

        assert result.exit_code == 0, result.output + " : " + str(result.exception)

        # Ensure DagsterCloudAgentInstance configured correctly
        assert call_instance[0].dagster_cloud_agent_token == TEST_TOKEN
        assert call_instance[0].dagster_cloud_api_headers.get(DEPLOYMENT_NAME_HEADER) == "staging"
        assert call_instance[0].dagster_cloud_url == "https://hooli.agent.dagster.cloud"
        assert call_instance[0].dagster_cloud_api_agent_label == None

    # With agent label
    with mock.patch("dagster_cloud.agent.cli.DagsterCloudAgent.run_loop", mock_run_loop):
        result = runner.invoke(
            app,
            ["--agent-token", TEST_TOKEN, "--deployment", "prod", "--agent-label", "My Test Agent"],
        )

        assert result.exit_code == 0, result.output + " : " + str(result.exception)

        assert call_instance[0].dagster_cloud_agent_token == TEST_TOKEN
        assert call_instance[0].dagster_cloud_api_headers.get(DEPLOYMENT_NAME_HEADER) == "prod"
        assert call_instance[0].dagster_cloud_url == "https://hooli.agent.dagster.cloud"
        assert call_instance[0].dagster_cloud_api_agent_label == "My Test Agent"

    # Ensure they're required, to test supplying config via CLI arg
    def mock_config_type():
        return {
            "networks": Field(Array(str), is_required=True),
            "env_vars": Field(
                [str],
                is_required=True,
                description="The list of environment variables names to forward to the docker container",
            ),
        }

    # With custom user code launcher
    with mock.patch(
        "dagster_cloud.agent.cli.DagsterCloudAgent.run_loop", mock_run_loop
    ), mock.patch(
        "dagster_cloud.workspace.docker.DockerUserCodeLauncher.config_type", mock_config_type
    ):
        result = runner.invoke(
            app,
            [
                "--agent-token",
                TEST_TOKEN,
                "--deployment",
                "prod",
                "--agent-label",
                "My Test Agent",
                "--user-code-launcher",
                "dagster_cloud.workspace.docker.DockerUserCodeLauncher",
                "--user-code-launcher-config",
                json.dumps(
                    {
                        "networks": ["abc", "def"],
                        "env_vars": ["PATH", "DAGSTER_HOME"],
                    }
                ),
            ],
        )

        assert result.exit_code == 0, result.output + " : " + str(result.exception)

        assert call_instance[0].dagster_cloud_agent_token == TEST_TOKEN
        assert call_instance[0].dagster_cloud_api_headers.get(DEPLOYMENT_NAME_HEADER) == "prod"
        assert call_instance[0].dagster_cloud_url == "https://hooli.agent.dagster.cloud"
        assert isinstance(call_instance[0].user_code_launcher, DockerUserCodeLauncher)
        assert call_instance[0].user_code_launcher.env_vars == ["PATH", "DAGSTER_HOME"]
