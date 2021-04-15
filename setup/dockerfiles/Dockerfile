FROM ubuntu:focal

RUN apt-get update && apt-get upgrade -y && apt-get install git python3 python3-pip sudo wget unzip -y && export DEBIAN_FRONTEND=noninteractive && apt-get -yq install glib2.0

RUN apt-get install vim nano tmux -y # unnecessary, but useful if need to do things inside docker container

COPY . /shepsetup

RUN mv /shepsetup/run-python-scripts /bin/run

RUN pip3 install -r /shepsetup/requirements.txt && /shepsetup/installlcm

CMD ["/usr/bin/echo", "Success! I like cheese"]

