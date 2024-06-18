# Base image to use, this must be set as the first line
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

WORKDIR /root

ENV http_proxy="http://10.15.22.49:7810"
ENV https_proxy="http://10.15.22.49:7810"
RUN apt-get -y update && apt-get install -y python3-pip git openssh-server curl nodejs npm
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir /var/run/sshd
RUN echo 'root:quantum123456' | chpasswd
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo "service ssh restart" >> ~/.bashrc

RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN rm packages-microsoft-prod.deb
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN apt-get update
RUN apt-get install -y dotnet-sdk-6.0

RUN git clone https://github.com/NWU-NISL-Fuzzing/UPBEAT.git
RUN pip install gdown numpy z3-solver jupyter matplotlib scipy tabulate
RUN gdown --id 112cRelito9MXYyzeL_ofwUUSUqaCRfKP
RUN unzip -q qsharp-compiler-28.zip

RUN echo "export PYTHONPATH=$PYTHONPATH:/root/UPBEAT/src/:/root/UPBEAT/src/Generate:/root/UPBEAT/src/Fuzzing" >> ~/.bashrc
