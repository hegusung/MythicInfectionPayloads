+++
title = "jscript_download_save_execute"
chapter = false
weight = 100
+++

## jscript_download_save_execute

This is a "Downloader" payload type, meaning it will fetch the payload from a url.
It is NOT an agent

### Downloader
  
This downloader will download a payload using a specific COM object, store it on disk and execute it using anothe COM object

Parameters:
- url: URL where the payload is located
- path: Where to store on disk, Environment variables are supported
- download_method: COM object to use to download the payload
- exec_method: COM object to execute the payload

### Author

- [@hegusung](https://github.com/hegusung)
