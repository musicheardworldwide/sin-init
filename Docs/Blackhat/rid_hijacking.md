# Windows RID Hijacking Attack

### Description

The RID Hijacking is a post-exploitation vector which allows stealthy persistence on **all Windows versions**. By using only OS [[sin/Initialization/Docs/Blackhat/Resources|Resources]],
this attack will create an entry on the target by modifying some properties of an existing account. It will change the account attributes by setting a Relative Identifier (RID), 
which should be owned by one existing account on the destination machine.

Taking advantage of some Windows Local Users Management integrity issues, this hook will allow to authenticate with one known account credentials (like GUEST account), and access with the privileges 
of another existing account (like ADMINISTRATOR account), even if the spoofed account is _*disabled*_.

#### Metasploit Module

*msf> use post/windows/manage/rid_hijack*

<p align="center">
  <img src="https://github.com/r4wd3r/RID-Hijacking/blob/master/rid_hijack.png" height="50%" weight="50%">
</p>

For more [[sin/Initialization/Docs/Open WebUI Docs/Information/Information]] see [csl.com.co](http://csl.com.co/rid-hijacking/).

### Categories
* Windows Persistence
* Post Exploitation
* [[sin/Initialization/Docs/Blackhat/ethical hacking/ethical hacking]]

### Black Hat sessions
[![Arsenal](https://github.com/toolswatch/badges/blob/master/arsenal/usa/2018.svg)](https://www.toolswatch.org/2018/05/black-hat-arsenal-usa-2018-the-w0w-lineup/)

### Code
https://github.com/r4wd3r/RID-Hijacking

### Lead Developer(s)
 Sebastián Castro (@r4wd3r)

### Social Media
* [Twitter](https://twitter.com/r4wd3r)
* [Github](https://github.com/r4wd3r)
----
