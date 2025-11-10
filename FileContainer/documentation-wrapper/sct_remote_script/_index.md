+++
title = "sct_remote_script"
chapter = false
weight = 100
+++

## sct_remote_script

This is a "Downloader" payload type, meaning it will fetch the payload from a url.
It is NOT an agent

### Downloader
  
This downloader will download a remote JScript or VBScript file and execute its content

Parameters:
- url: URL where the JScript or VBScript payload is located
- script_type: script type (JScript, VBScript, JScript.Encode, VBScript.Encode)

### Author

- [@hegusung](https://github.com/hegusung)
