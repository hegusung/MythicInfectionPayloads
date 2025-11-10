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

class url_payload(PayloadType):
    name = "url_payload"
    file_extension = "url"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = False
    wrapped_payloads = []
    note = """Creates a URL file"""
    supports_dynamic_loading = True
    c2_profiles = []
    mythic_encrypts = True
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "clickable"
    agent_icon_path = agent_path / "agent_functions" / "click.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "url",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="URL the file will point to",
        ),
        BuildParameter(
            name = "icon",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Icon to setup, leave not to set the Icon parameter",
        ),
        BuildParameter(
            name = "icon_index",
            parameter_type=BuildParameterType.Number,
            default_value=0,
            description="IconIndex parameter",
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
            icon = self.get_parameter('icon')
            icon_index = self.get_parameter('icon_index')

            payload = """[InternetShortcut]
URL={url}"""

            if len(icon) != 0:
                payload += """
IconFile={icon}
IconIndex={icon_index}
"""

            resp.payload = payload.format(url=url, icon=icon, icon_index=icon_index)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
