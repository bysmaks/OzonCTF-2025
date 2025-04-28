#!/bin/bash
cd /home/ctf
socat tcp4-listen:13337,fork exec:./server.py
