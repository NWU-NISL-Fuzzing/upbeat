## Docker image

We provide a [docker image]() to run "out of box". 

## Setup environment without Docker

To set up Upbeat in your environment, ensure the following prerequisites are met:

**1.Install dotnet.**

(1)Download dotnet-install.sh.

```
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
```

(2)Run dotnet-install.sh. 

```
chmod +x ./dotnet-install.sh
./dotnet-install.sh --channel 6.0
```

(3)Configure. 

```
echo "export DOTNET_ROOT=$HOME/.dotnet \
export PATH=$PATH:$HOME/.dotnet:$HOME/.dotnet/tools \
" >> ~/.bashrc
source ~/.bashrc
```

**2.Install QDK template.**

```
dotnet new --install Microsoft.Quantum.ProjectTemplates::0.24.210930
```

**3.Install dotnet-coverage.**

```
dotnet tool install -g dotnet-coverage
```

**4.Set PYTHONPATH.**

Open the configure file. 

```
vim ~/.bashrc
```

Add the following content.

```
export PYTHONPATH=[path]/UPBEAT/src:[path]/UPBEAT/src/Generate:[path]/UPBEAT/src/Fuzzing:$PYTHONPATH
```

Refresh the configure file.

```
source ~/.bashrc
```

**5.Install pip tools.**

Before using UPBEAT, some pip tools are necessary.

```
pip install six numpy 
```

**6.Download the Q# compiler build from source.**

We upload the instrumented repository on [this link](https://drive.google.com/file/d/112cRelito9MXYyzeL_ofwUUSUqaCRfKP/view?usp=drive_link), please download it and unzip it into `/root`.
