import logging
import pathlib
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import os

import tempfile
import pyminizip
import py7zr
import pycdlib
import cabarchive


class PackMyPayload(PayloadType):
    name = "packmypayload"
    file_extension = "archive"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["*"]
    note = """PackMyPayload"""
    translation_container = None # "myPythonTranslation"
    build_parameters = [
        BuildParameter(
            name="archive_type",
            required=True,
            parameter_type=BuildParameterType.ChooseOne,
            choices=["zip", "7z", "iso", "cab"],
            description="Archive type",
            default_value="zip"
        ),
        BuildParameter(
            name="password",
            required=True,
            parameter_type=BuildParameterType.String,
            description="Archive password (zip and 7z only)",
            default_value=""
        ),
        BuildParameter(
            name="payload_name",
            required=True,
            parameter_type=BuildParameterType.String,
            description="Payload name in the archive",
            default_value="payload.ext"
        ),
        BuildParameter(
            name = "file1",
            parameter_type=BuildParameterType.String,
            description="File name to add to the archive",
        ),
        BuildParameter(
            name = "file1_content",
            parameter_type=BuildParameterType.File,
            description="File content to add to the archive",
        ),

    ]
    agent_path = pathlib.Path(".") / "archive"
    agent_icon_path = agent_path / "agent_functions" / "archive.svg"
    agent_code_path = agent_path / "agent_code"

    build_steps = [
    ]

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        # create the payload
        build_msg = ""

        try:
            archive_type = self.get_parameter("archive_type")
            payload_name = self.get_parameter("payload_name")
            password = self.get_parameter("password")


            output = "/tmp/output."
            if archive_type == "zip":
                output += "zip"
            elif archive_type == "7z":
                output += "7z"
            elif archive_type == "iso":
                output += "iso"
            elif archive_type == "cab":
                output += "cab"
            else:
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "Unsupported archive type: %s" % archive_type
                return resp

            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save payload
                print(os.path.join(temp_dir, payload_name))
                f = open(os.path.join(temp_dir, payload_name), "wb")
                f.write(self.wrapped_payload)
                f.close()

                for i in range(1,2):
                    filename = self.get_parameter("file%d" % i)
                    if filename:
                        file_id = self.get_parameter("file%d_content" % i)
                        exportData = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(
                            AgentFileId=file_id
                        ))
                        if not exportData.Success:
                            resp.build_stderr = exportData.Error
                            resp.set_status(BuildStatus.Error)
                            return resp

                        f = open(os.path.join(temp_dir, filename), "wb")
                        f.write(exportData.Content)
                        f.close()


                if archive_type == "zip":
                    pack_zip(temp_dir, output, password)
                elif archive_type == "7z":
                    pack_7z(temp_dir, output, password)
                elif archive_type == "iso":
                    pack_iso(temp_dir, output)
                elif archive_type == "cab":
                    pack_cab(temp_dir, output)
            
            f = open(output, "rb")
            archive_data = f.read()
            f.close()

            try:
                os.remove(output)
            except:
                pass

            resp.payload = archive_data
            resp.build_message = "Successfully built!\n"
        except Exception as e:
            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp


def pack_zip(temp_dir, outfile, password):
    # Gather all file paths from the temp directory
    infiles = []
    outfiles = []

    for root, _, files in os.walk(temp_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = "/" + os.path.relpath(full_path, start=temp_dir)  # keep relative path inside ZIP
            infiles.append(full_path)
            outfiles.append(os.path.dirname(arcname))

    compression_level = 5

    pyminizip.compress_multiple(infiles, outfiles, outfile, password, compression_level)

def pack_7z(temp_dir, outfile, password):
    if len(password) == 0:
        password = None

    # Create 7z archive
    with py7zr.SevenZipFile(outfile, 'w', password=password) as archive:
        archive.writeall(temp_dir, arcname="")

def pack_iso(temp_dir, outfile):
    iso = pycdlib.PyCdlib()
    iso.new(joliet=3)


    for root, dirs, files in os.walk(temp_dir):
        for d in dirs:
            dir_path = os.path.join(root, d)
            joliet_path = os.path.relpath(dir_path, temp_dir).replace('\\', '/')
            iso.add_directory(joliet_path=f'/{joliet_path}')

        for f in files:
            file_path = os.path.join(root, f)
            joliet_path = os.path.relpath(file_path, temp_dir).replace('\\', '/')

            iso.add_file(file_path, joliet_path=f'/{joliet_path};1')


    iso.write(outfile)
    iso.close()

def pack_cab(temp_dir, outfile):

    try:
        arc = cabarchive.CabArchive()

        for root, _, files in os.walk(temp_dir):
            for file in files:
                abs_path = os.path.join(root, file)

                # Get relative path inside archive
                rel_path = os.path.relpath(abs_path, start=temp_dir)
                rel_path = rel_path.replace("\\", "/")  # Normalize for CAB format

                print(f'Adding file: {abs_path} as {rel_path}')

                with open(abs_path, 'rb') as f:
                    arc[rel_path] = cabarchive.CabFile(f.read())

        with open(outfile, 'wb') as out_f:
            out_f.write(arc.save())

        return True

    except Exception as e:
        print(f'[!] Failed to create CAB: {e}')
        return False
