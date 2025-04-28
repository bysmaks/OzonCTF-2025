FROM python:3.11

RUN apt-get update -yyq # && apt-get upgrade -yyq
RUN apt install socat -yyq

WORKDIR /code

COPY . /code/

RUN chmod +x entrypoint.sh task.py
ENTRYPOINT [ "./entrypoint.sh" ]
