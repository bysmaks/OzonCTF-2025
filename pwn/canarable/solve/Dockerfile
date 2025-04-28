FROM tuhfox/ozon-ctf:latest

RUN apt-get -y update
RUN apt-get -y install socat

RUN useradd -m ctf
USER ctf
WORKDIR /home/ctf
COPY exploit  /home/ctf
EXPOSE 37373
CMD socat tcp-listen:37373,reuseaddr,fork exec:"./exploit"
