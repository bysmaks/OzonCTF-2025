FROM ubuntu:24.04

RUN apt -y update
RUN apt -y install python3
RUN apt -y install libicu-dev
RUN apt -y install libatomic1
RUN apt -y install libstdc++6
RUN apt -y install socat

RUN useradd -m ctf
RUN echo "ctf:ctf" | chpasswd
WORKDIR /home/ctf

ADD d8 /home/ctf
ADD server.py /home/ctf
ADD snapshot_blob.bin /home/ctf
ADD run.sh /home/ctf
ADD flag.txt /flag
ADD catflag /catflag
RUN chown -R root:root /home/ctf
RUN chmod -R 555 /home/ctf

RUN chown root:root /flag && chmod 400 /flag
RUN chown root:root /catflag && chmod 755 /catflag && chmod u+s /catflag

USER ctf
EXPOSE 13337
CMD "./run.sh"
