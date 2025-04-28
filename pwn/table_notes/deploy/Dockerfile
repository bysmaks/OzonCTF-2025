FROM ubuntu:24.04

RUN apt-get -y update
RUN apt-get -y install socat

RUN useradd -m ctf

USER ctf
WORKDIR /home/ctf
COPY table_notes  /home/ctf
COPY flag  /home/ctf
EXPOSE 3773
CMD socat tcp-listen:3773,reuseaddr,fork exec:"./table_notes"
