+++
title = "cmd_to_lnk"
chapter = false
weight = 100
+++

## cmd_to_lnk

### Wrapper
  
This wrapper allows to create a LNK file within Mythic. The input is a cmd payload, this script will split the binary from the arguments and insert them in the LNK

The parameters are as follows:
- description: LNK file description field
- icon_file: Icon path, must be already present in the targeted system to display properly
- window_mode: Defines if you want the Window to be minimized during the LNK execution
- work_dir: Defines the LNK workdir 

### Author

- [@hegusung](https://github.com/hegusung)

Original Github project:
- https://github.com/strayge/pylnk
