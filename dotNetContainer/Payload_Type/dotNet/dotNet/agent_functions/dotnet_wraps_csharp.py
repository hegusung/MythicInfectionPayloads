import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import subprocess
import json
import string
import os
import shutil
import base64
import random

from io import BytesIO
from pathlib import Path
import zipfile


class dotnet_wraps_csharp(PayloadType):
    name = "dotnet_wraps_csharp"
    file_extension = "dotnet"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["csharp"]
    note = """Compiles a C-sharp file to a dotNet exe or dll"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "dotNet"
    agent_icon_path = agent_path / "agent_functions" / "dotnet.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "type",
            parameter_type=BuildParameterType.ChooseOne,
            choices=["WinExe", "Library"],
            default_value="WinExe",
            description="dotNet binary type",
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
            cs_code = self.wrapped_payload

            bin_type = self.get_parameter("type")

            dotnet_dir = "/tmp/dotnetbin"

            try:
                shutil.rmtree(dotnet_dir)
            except:
                pass

            os.makedirs(dotnet_dir, exist_ok=True)

            with open(os.path.join(dotnet_dir, "Program.cs"), "wb") as f:
                f.write(cs_code)

            if bin_type in ["Exe", "WinExe"]:
                subprocess.run(["mcs", "-out:prog.exe", "-target:winexe", "Program.cs", "-unsafe"], cwd=dotnet_dir, check=True)

                with open(os.path.join(dotnet_dir, "prog.exe"), "rb") as f:
                    payload = f.read()

            elif bin_type == "Library":
                cmd_parts = ["mcs", "-out:prog.dll", "Program.cs", "-unsafe", "-target:library"]
                if b"using System.Configuration.Install;" in cs_code:
                    cmd_parts += ["-r", "System.Configuration.Install"]

                subprocess.run(cmd_parts, cwd=dotnet_dir, check=True)

                with open(os.path.join(dotnet_dir, "prog.dll"), "rb") as f:
                    payload = f.read()

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp

