FROM tuhfox/ozon-ctf:latest

RUN apt-get -y update
RUN apt-get -y install socat

RUN useradd -m ctf
USER ctf
WORKDIR /home/ctf
COPY main  /home/ctf
COPY flag  /home/ctf

EXPOSE 17171
CMD socat tcp-listen:17171,reuseaddr,fork exec:"./main"
