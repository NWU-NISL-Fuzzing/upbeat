# Artifacts Evaluation Instructions

This document provides instructions for the artifact evaluation of our accepted paper "Upbeat: Test Input Checks of Q# Quantum Libraries". We provide two ways to run Upbeat: an online jupyter notebook on a cloud server, and a Docker image for local use.

**Disclaim:** Although we have worked hard to ensure our AE scripts are robust, our tool remains a research prototype. It can still have glitches when used in complex, real-life settings. If you discover any bugs, please raise an issue, describing how you ran the program and what problem you encountered. We will get back to you ASAP. Thank you.

# Step-by-Step Instructions

### 1 Jupyter Notebook

We provide an interactive Jupyter Notebook hosted on a cloud server. The notebook first uses a single case to demonstrate the entire Upbeat pipeline. Then, it conducts small-scale testing (100 test cases) and finally reproduces the evaluation presented in our paper. 

Please click [this link]() to access our notebook.

### 2 Docker Image

#### 2.1 Create a Docker container

We offer a ready-to-use [image](https://hub.docker.com/repository/docker/weucodee/upbeat/general), which contains the pre-build environment, a detailed document, and the source code of Upbeat. 

```
docker pull weucodee/upbeat:latest
```

Alternatively, users can also run the [Dockerfile](build/Dockerfile). 

```
docker build -t upbeat:v1 .
```

Then, create a Docker container. There are two ports that should be mapped: the 22 port (for SSH) and the 8888 port (for local Jupyter Notebook). 

```
docker run -d -it -p [XXX]:22 -p [XXX]:8888 upbeat:v1
```

#### 2.2 Run

(Optional) Adjust [the configuration file](src/config.json) to align with users' specific requirements. Below are the configurable parameters and their descriptions:

```
work_dir:               The directory path where the repository is located.
fragment_num:           The number of code fragments to generate test cases.
level:                  Time to combine code fragments. The default is set to 1.
ingredient_table_name : Table name of code fragments,
reference_db:           Path to the API constraint database.
corpus_db:              Path to the code fragment database.
history_db:             Path to the historical bug database.
result_db:              Path of the result database.
temp_project:           Path to the Q# projects used during the testing phase.
boundary_value:         Special values for random input generation.
```

**Step1. Generate test cases.**

```
cd upbeat/src/Generate
python main.py
```

_(Approximate 2 seconds for 100 test cases.)_

There are two steps in test case generation: (1) assemble code segments and (2) generate callable inputs. All generated test cases are stored in `result_db`.

PS. `fragment_num` does not necessarily correspond to the number of test cases. For example, if a fragment contains constraints, Upbeat will generate two test cases. If there are no constraints, only one test case will be generated.

**Step2. Execute test cases.**

```
cd ../Fuzzing
python hybrid_testing.py
```

_(Approximate 50 minuts for 100 test cases.)_

Each test case will first be applied on language-level testing, with execution information stored in table `originResult_cw`. If any anomalies occur, relevant information will be logged in table `differentialResult_cw`. 

If no anomalies are detected, the test case proceeds to differential testing, where results are stored in table `differentialResult_sim`.

Users can also execute these two steps separately by running the following command:

```
python boundary_value_testing.py
python differential_testing.py
```

**Step3. Filter anomalies.**

```
python history_bug_filter.py
```

UPBEAT is capable of filtering the anomalies into three types: (1) bugs that have already been analyzed (save in `bug.txt`), (2) faulty that have already been analyzed (save in `faulty.txt`), (3) new anomalies awaiting verification (save in `new_anomalies.txt`). 

#### 2.3 Experimental Result

+ (RQ1) The bug data can be found in [this page](data/result/BugList.md). 
+ (RQ2) The coverage data is organized into two folders, [one](data/experiment/cov-result-origin) stores the original coverage values of four libraries, and [another](data/experiment/cov-result-calculated) stores the calculated weighted averages of coverage.
+ (RQ2) The anomalous behaviors found by baseline methods and Upbeat. Anomalous detected via language-level testing are stored in [this folder](data/experiment/anomalies-lang), and ones via differential testing are stored in [this folder](data/experiment/anomalies-diff).
+ (RQ3) The results of the ablation study can be found in [this folder](data/experiment/ablation-study).
+ (RQ4) The evaluation of constraint extraction can be found in [this folder](data/experiment/constraint-extraction).

#### 2.4 Jupyter Notebook

To run the notebook on your computer, follow the following steps:

```
cd jupyter
jupyter notebook --ip=[YOUR_IP] --port=8888 --allow-root
```

This will open the notebook in your default web browser, allowing you to interact with it seamlessly.

**Help:** If you are using a Docker container, you can find the IP address by running `cat /etc/hosts`.

# Troubleshooting

Here are some issues we've encountered when installing and running Upeat on different devices. We hope [this page](build/CommonIssues.md) can help you resolve them.
