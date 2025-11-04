+++
title = "script_to_sct"
chapter = false
weight = 100
+++

## script_to_sct

### Wrapper

This wrapper converts a JScript or VBScript payload as a SCT file.

SCT files can in turn be executed by LOLBAs such as regsvr32.exe or by scripting languages such as powershell

To use with regsvr32.exe, you must define a progid (this will create the <registration> part of the payload)

Arguments: 
- progid: Defined the progid parameter of the <registration> payload
- classid: Defined the classid parameter of the <registration> payload
  

### Author

- [@hegusung](https://github.com/hegusung)

