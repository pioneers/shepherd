FROM ubuntu:focal

RUN apt-get update && apt-get upgrade -y && apt-get install git python3 python3-pip sudo wget unzip -y && export DEBIAN_FRONTEND=noninteractive && apt-get -yq install glib2.0

COPY . /shepsetup

RUN pip3 install -r /shepsetup/requirements.txt && /shepsetup/installlcm

CMD ["/bin/bash"]
