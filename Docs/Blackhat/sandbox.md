# Sandbox

### Description
Sandbox provides a simple way to enable basic `seccomp` [system call filtering][[[tools-export-1745623456262.json]]] in any application on Linux (even proprietary one) via environment variables. It is very similar to `SystemCallFilter=` [functionality in systemd][[[02-05-2025]]], but with some advantages:

  * it doesn't have some of `systemd` limitations:
    > the execve, exit, exit_group, getrlimit, rt_sigreturn, sigreturn system calls and the system calls for querying [[sin/Initialization/Tools/MCP Server Tools/Time/time]] and sleeping are implicitly whitelisted...
  * it can provide tighter filtering for dynamically linked binaries

### Categories
* Hardening

### Black Hat sessions
[![Arsenal](https://github.com/toolswatch/badges/blob/master/arsenal/usa/2022.svg)](https://www.blackhat.com/us-22/arsenal/schedule/index.html#sandboxing-in-linux-with-zero-lines-of-code-27289)

### Code
https://github.com/cloudflare/sandbox

### Lead Developer(s)
 Ignat Korchagin - Cloudflare https://github.com/cloudflare

### Social Media
* [Twitter](https://twitter.com/ignatkn)
* [Company Website](https://cloudflare.com/)

[[[tools-export-1745623456262.json]]]: http://man7.org/linux/man-pages/man2/seccomp.[[02-05-2025]].html
[[[02-05-2025]]]: https://www.freedesktop.org/software/systemd/man/systemd.exec.html#SystemCallFilter=
