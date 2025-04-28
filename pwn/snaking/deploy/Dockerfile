FROM ubuntu:24.04@sha256:72297848456d5d37d1262630108ab308d3e9ec7ed1c3286a32fe09856619a782

ENV LC_CTYPE=en_US.UTF-8 PYTHONPATH=/home/ctf
RUN apt-get -y update && apt-get -y install socat libseccomp2

RUN useradd -m ctf

COPY getflag /
RUN chmod 111 /getflag

COPY python.tar.gz .
RUN tar xzf python.tar.gz && rm python.tar.gz
RUN ln -s /python/bin/python3 /usr/bin/python3

WORKDIR /home/ctf

COPY server.py .
COPY bitset.so .
RUN chown -R root:root /home/ctf
RUN chmod -R 555 /home/ctf

USER ctf

CMD ["socat", "tcp-l:11331,reuseaddr,fork", "exec:./server.py"]
