#!/usr/bin/env python3
import string

print("BIM BIM:")

glob = vars(__builtins__).copy()
for var in ('input','open','exec','eval','getattr','__import__','__builtins__','globals'):glob[var] = None
inp = input("> ")
allowed_chars = string.ascii_letters + string.digits + "'*,+()"
if any(char not in allowed_chars for char in inp) or len(inp) > 100 or 'flag' in inp:
    print("NONONO MISTER FISH YOU NEED TO READ PYTHON SOURCE CODE")
    exit()
print(eval(inp, glob))

