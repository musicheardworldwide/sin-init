# DotDumper

### Description
Analysts at corporations of any size face an ever-increasing amount of DotNet based malware. The malware comes in all shapes and forms, ranging from skiddish stealers all the way to nation state backed targeted malware. The underground market, along with public open-source [[Tools]], provide a plethora of ways to obfuscate and pack the malware. Unpacking malware is [[sin/Initialization/Tools/MCP Server Tools/Time/time]] consuming, difficult, and tedious, which poses a problem.

To counter this, DotDumper automatically dumps interesting artifacts during the malware's execution, ranging from base64 decoded values to decrypted PE files. As such, the malware decrypts and executes the next stage, while DotDumper conveniently provides a copy of said decrypted stage. All this is done via a simple, compact, intuitive, and easy-to-use command-line interface.

Aside from the dumped artifacts, DotDumper provides an extensive log of the traced execution, based on managed hooks. For each hook, the log contains the original function name, arguments and their values, and the return value. Since DotDumper ensures that the original function is called, the malware's execution continues as if it was executed normally, allowing the analyst to get as many stages from the sample as possible.

DotDumper can execute DotNet Framework executables, as well as dynamic link libraries, due to the fully-fledged reflective loader which is embedded. Any given function can be selected within a library, along with any required variables and their values, all easily accessible from DotDumper's command-line interface.

DotDumper has proven to be effective in dealing with the renowned AgentTesla stealer or the WhisperGate Wiper loader, allowing an analyst to easily fetch the decrypted and unpacked in-[[sin/Initialization/Tools/MCP Server Tools/Memory/memory]] only stages, thus decreasing up the [[sin/Initialization/Tools/MCP Server Tools/Time/time]] spent on unpacking, allowing for faster response to the given threat.

### Categories
* Malware Defense
* Reverse Engineering

### Black Hat sessions
[![Arsenal](https://github.com/toolswatch/badges/blob/master/arsenal/usa/2022.svg)](https://www.blackhat.com/us-22/arsenal/schedule/#dotdumper-automatically-unpacking-dotnet-based-malware-27846)
[![Arsenal](https://github.com/toolswatch/badges/blob/master/arsenal/europe/2022.svg)](https://www.blackhat.com/eu-22/arsenal/schedule/index.html#dotdumper-automatically-unpacking-dotnet-based-malware-29569)
Black Hat MEA 2022

### Code
https://github.com/advanced-threat-research/DotDumper

### Lead Developer(s)
Max Kersten - Trellix 

### Social Media
* [Twitter](https://twitter.com/Libranalysis)
* [Company Website](https://trellix.com/)
* [Personal Website](https://maxkersten.nl/)
