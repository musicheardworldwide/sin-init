# Malboxes

### Description
Malboxes is a tool to streamline and simplify the creation and management of
virtual machines used for malware analysis.

Building analysis machines is a tedious task. One must have all the proper
[[Tools]] installed on a VM such as a specific version of vulnerable software (ie:
Flash), Sysinternal [[Tools]], debuggers (Windbg), network traffic analyzers
(Wireshark), man-in-the-middle [[Tools]] (Fiddler). One must also avoid leaking
his precious proprietary software licenses (IDA). At the moment, this menial
job is not automated and is repeated by every analyst.

Malboxes leverages the DevOps principle of infrastructure as code to enable
researchers to automatically create fully operational and reusable analysis
machines. The tool uses Vagrant and Packer to do an initial out-of-band
bootstrapping. Afterward, chocolatey is used to install further [[Tools]]
benefiting from the chocolatey package repository.

Attendees will learn a simple tool for safe malware analysis practice that is
easy to grasp, enabling them to start doing analysis faster. Seasoned malware
researchers will also gain from this demo by seeing how the DevOps approach
can be applied to simplify and accelerate their labs' malware
reverse-engineering capacity or reduce its management overhead.


### Categories
* Malware Research

### Black Hat sessions

[![Arsenal](https://github.com/toolswatch/badges/blob/master/arsenal/usa/2017.svg)](https://www.toolswatch.org/2017/06/the-black-hat-arsenal-usa-2017-phenomenal-line-up-announced/)

### Code
https://github.com/GoSecure/malboxes

### Lead Developer(s)
 Olivier Bilodeau - GoSecure ([GitHub](https://github.com/obilodeau), [Twitter](https://twitter.com/obilodeau))

### Social Media
* [Blog posts, videos and presentations](https://github.com/GoSecure/malboxes#more-information)
* [Company Twitter](https://twitter.com/gosecure_inc)
* [Company Website](https://gosecure.net/)
* [Company GitHub](https://github.com/GoSecure)

