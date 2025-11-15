import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os


class lolbas_exec_csproj(PayloadType):
    name = "lolbas_exec_csproj"
    file_extension = "cmd"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    note = """Execute a csproj file via msbuild"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "cmd"
    agent_icon_path = agent_path / "agent_functions" / "cmd.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "lolbas",
            parameter_type=BuildParameterType.ChooseOne,
            choices=["msbuild"], 
            description="LOLBAS to use",
        ),
        BuildParameter(
            name = "binary",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Override binary path",
        ),
        BuildParameter(
            name = "csproj_path",
            parameter_type=BuildParameterType.String,
            description="csproj file Path",
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
            lolbas = self.get_parameter('lolbas')
            binary = self.get_parameter('binary')
            csproj_path = self.get_parameter('csproj_path')

            if len(binary) == 0:
                if lolbas == "msbuild":
                    binary = "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"

            if lolbas == "msbuild":
                payload = "%s %s" % (binary, csproj_path)

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
