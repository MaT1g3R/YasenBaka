FROM python:3.6-stretch
MAINTAINER MaT1g3R

ENV PYTHONUNBUFFERED 1

RUN echo "deb http://ftp.uk.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y software-properties-common swig libssl-dev dpkg-dev ffmpeg texlive netpbm poppler-utils

RUN mkdir /code
WORKDIR /code
COPY . /code/

RUN pip install -U pip
RUN pip install -Ur requirements.txt

CMD ["/code/run.sh"]
