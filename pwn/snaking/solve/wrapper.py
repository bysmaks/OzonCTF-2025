from pwn import args, connect

spl = open('exploit.py').read()

io = connect(args.HOST or '127.0.0.1', args.PORT or 11331)
io.sendlineafter(b': ', str(len(spl)).encode())
io.sendafter(b': ', spl.encode())
io.interactive()
