FROM ubuntu:24.04

RUN apt-get -y update
RUN apt-get -y install socat

RUN useradd -m ctf

USER ctf
WORKDIR /home/ctf
COPY muggy  /home/ctf
COPY flag  /home/ctf
EXPOSE 1773
CMD socat tcp-listen:1773,reuseaddr,fork exec:"./muggy"