# Shoggoth: Asmjit Based Polymorphic Encryptor

### Description
Shoggoth is an open-source project based on C++ and asmjit library used to encrypt given shellcode, PE, and COFF files polymorphically.

Shoggoth will generate an [[sin/Initialization/Docs/Prompting Guides/output]] file that stores the payload and its corresponding loader in an obfuscated form. Since the content of the [[sin/Initialization/Docs/Prompting Guides/output]] is position-independent, it can be executed directly as a shellcode. While the payload is executing, it decrypts itself at runtime. In addition to the encryption routine, Shoggoth also adds garbage instructions, that change nothing, between routines.

Current features are listed below:

- Works on only x64 inputs
- Ability to merge PIC COFF Loader with COFF or BOF input files
- Ability to merge PIC PE Loader with PE input files
- Stream Cipher with RC4 Algorithm
- Block Cipher with randomly generated operations
- Garbage instruction generation

### Categories
* Malware Offense

### Black Hat sessions
[![Arsenal](https://github.com/toolswatch/badges/blob/master/arsenal/europe/2022.svg)](https://www.blackhat.com/eu-22/arsenal/schedule/index.html#shoggoth-asmjit-based-polymorphic-encryptor-29588)

### Code
https://github.com/frkngksl/Shoggoth

### Lead Developer(s)
 Furkan Göksel

### Social Media
* [Twitter](https://twitter.com/R0h1rr1m)
* [Github](https://github.com/frkngksl)
* [Personal Website](https://frkngksl.github.io/)
