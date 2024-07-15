# Base image to use, this must be set as the first line
FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

WORKDIR /root

RUN apt-get -y update && \
    apt-get install -y python3-pip git openssh-server curl nodejs npm zip vim screen
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir /var/run/sshd
RUN echo 'root:upbeat2024' | chpasswd
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo "service ssh restart" >> ~/.bashrc

RUN wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb
RUN apt-get update && \
    apt-get install -y apt-transport-https
RUN apt-get update && \
    apt-get install -y dotnet-sdk-6.0
RUN dotnet tool install -g dotnet-coverage
RUN dotnet new -i Microsoft.Quantum.ProjectTemplates
RUN dotnet new -i Microsoft.Quantum.ProjectTemplates::0.24.210930

RUN git clone https://github.com/NWU-NISL-Fuzzing/upbeat.git

RUN pip install gdown numpy z3-solver jupyter matplotlib scipy tabulate pandas

RUN gdown --id 112cRelito9MXYyzeL_ofwUUSUqaCRfKP && \
    unzip -q qsharp-compiler-28.zip && \
    rm qsharp-compiler-28.zip

RUN gdown --id 11gTUv4vpBE5OMZefZV6-Wp1DEPaHvo8A && \
    unzip -q -d /root/upbeat/data/experiment database-20240715-1.zip && \
    rm database-20240715-1.zip

RUN echo "export PYTHONPATH=$PYTHONPATH:/root/upbeat/src/:/root/upbeat/src/Generate:/root/upbeat/src/Fuzzing" >> ~/.bashrc
