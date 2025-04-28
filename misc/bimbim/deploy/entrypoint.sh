#!/bin/sh

while true; do
    socat TCP-LISTEN:9235,reuseaddr,fork EXEC:"timeout -s SIGKILL 10 ./task.py"
done
