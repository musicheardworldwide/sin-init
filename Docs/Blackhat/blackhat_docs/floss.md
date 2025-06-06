# FireEye Labs Obfuscated String Solver (FLOSS)

### Description
The FireEye Labs Obfuscated String Solver (FLOSS) is an open source tool that automatically detects, extracts, and decodes obfuscated strings in Windows Portable Executable (PE) files. Malware analysts, forensic investigators, and incident responders can use FLOSS to quickly extract sensitive strings to identify indicators of compromise (IOCs). Malware authors encode strings in their programs to hide malicious capabilities and impede reverse engineering. Even simple encoding schemes defeat the ‘strings’ tool and complicate static and dynamic analysis. FLOSS uses advanced static analysis techniques, such as emulation, to deobfuscate encoded strings.

FLOSS is extremely easy to use and works against a large corpus of malware. It follows a similar invocation as the ‘strings’ tool. Users that understand how to interpret the strings found in a binary will understand FLOSS’s [[sin/Initialization/Docs/Prompting Guides/output]]. FLOSS extracts higher value strings, as strings that are obfuscated typically contain the most sensitive configuration [[sin/Initialization/Docs/Blackhat/Resources|Resources]] – including C2 server addresses, names of dynamically resolved imports, suspicious file paths, and other IOCs.

### Categories
* Malware analysis
* Malware research
* Reverse engineering

### Black Hat sessions
#### Arsenal USA 2016
[![Arsenal](https://rawgit.com/toolswatch/badges/master/arsenal/usa/2016.svg)](https://www.toolswatch.org/2016/06/the-black-hat-arsenal-usa-2016-remarkable-line-up/)

#### Arsenal Europe 2016
[![Arsenal](https://rawgit.com/toolswatch/badges/master/arsenal/europe/2016.svg)](https://www.toolswatch.org/2016/09/the-black-hat-arsenal-europe-2016-line-up/)

#### Arsenal Asia 2018
[![Arsenal](https://rawgit.com/toolswatch/badges/master/arsenal/asia/2018.svg)](https://www.toolswatch.org/2018/01/black-hat-arsenal-asia-2018-great-lineup/)

https://www.blackhat.com/asia-18/arsenal/schedule/

### Code 
https://github.com/fireeye/flare-floss

### Lead Developers
* William Ballenthin - @williballenthin
* Moritz Raabe - @m_r_tz

### Social Media 
* [@williballenthin](https://twitter.com/williballenthin)
* [@m_r_tz](https://twitter.com/m_r_tz)
* [FireEye Website](https://www.fireeye.com/) 

