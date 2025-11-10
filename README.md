# MythicInfectionPayloads

This project works with Mythic C2 and aims to create containers responsible of creating infection chains within Mythic

## Payload Types

- Wrappers: Wrappers are payloads which includes/pack/contains another payload
- Downloaders: Downloaders are payloads which downloads another payload from a url and processes it

Downloaders currently doesn't exist within mythic, they work my specifying a URL parameter

## Install

All the containers can be installed all at once using the following command:

```sh
./install.py --mythic-path /path/to/mythic
``` 

## Payloads

Currently the following payloads are implemented:

### Scripts

- psh_download_execute_psh
- psh_shellcode_execution
- jscript_download_save_execute
- encoded_script

### File formats

- cmd_to_lnk
- script_to_hta
- script_to_wsf
- script_to_sct

### LOLBas

- cmd_regsvr32_remote_sct
- powershell_to_cmd

### Archives

- packmypayload

### Phishing kits

- clickfix
- filefix

