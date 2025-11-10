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

class wsf_wraps_script(PayloadType):
    name = "wsf_wraps_script"
    file_extension = "wsf"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["jscript_download_save_execute"]
    note = """Creates a WSF payload from a JScript or VBScript script"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "clickable"
    agent_icon_path = agent_path / "agent_functions" / "click.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
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
            
            payload = """<?xml version="1.0" ?>
<job>
  <script language="{script_type}">
    <![CDATA[ 
        {script_payload}
    ]]>
  </script>
</job>"""

            resp.payload = payload.format(script_type=script_type, script_payload=script_payload)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
