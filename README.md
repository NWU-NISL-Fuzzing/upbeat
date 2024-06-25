# UPBEAT (Updating)

UPBEAT is a fuzzing tool to generate random test cases for bugs related to input checking in Q# libraries.

## Build Pre-requisites

### Use Docker

We offer a ready-to-use [image]() that runs "out of the box". Alternatively, users can also run the [Dockerfile](build/Dockerfile). 

```
docker build -t upbeat:v1 .
docker run -it upbeat:v1 bash
```

### Setup Locally

1. Ensure you have downloaded the following pip tools.
```
pip install gdown numpy z3-solver jupyter matplotlib scipy tabulate
```
2. Follow the installation instructions in [INSTALL.md](build/INSTALL.md).
3. Clone the repository.
```
git clone https://github.com/NWU-NISL-Fuzzing/UPBEAT.git
```

## Basic Usage

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
cd UPBEAT/src/Generate
python main.py
```

There are two steps in test case generation: (1) assemble code segments and (2) generate callable inputs. All generated test cases are stored in `result_db`.

PS. `fragment_num` does not necessarily correspond to the number of test cases. For example, if a fragment contains constraints, Upbeat will generate two test cases. If there are no constraints, only one test case will be generated.

**Step2. Execute test cases.**

```
cd ../Fuzzing
python hybrid_testing.py
```

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

## Jupyter Notebook

We provide two lightweight notebooks, a [demo notebook](jupyter/demo.ipynb) for a quick insight into all steps in Upbeat, and a [reproduction notebook](jupyter/reproduction.ipynb) to reproduce our experiment. Users can use our notebooks in two ways: launching it on their local machine or exploring it [online]().

To run the notebook on your computer, follow these simple steps:

```
cd jupyter
jupyter notebook --ip=[YOUR_IP] --port=8888 --allow-root
```

This will open the notebook in your default web browser, allowing you to interact with it seamlessly.

## Experimental Result

+ (RQ1) The bug data can be found in [this page](data/result/BugList.md). 
+ (RQ2) The coverage data is organized into two folders, [one](data/experiment/cov-result-origin) stores the original coverage values of four libraries, and [another](data/experiment/cov-result-calculated) stores the calculated weighted averages of coverage.
+ (RQ2) The anomalous behaviors found by baseline methods and Upbeat. Anomalous detected via language-level testing are stored in [this folder](data/experiment/anomalies-lang), and ones via differential testing are stored in [this folder](data/experiment/anomalies-diff).
+ (RQ3) The results of the ablation study can be found in [this folder](data/experiment/ablation-study).
+ (RQ4) The evaluation of constraint extraction can be found in [this folder](data/experiment/constraint-extraction).

## Troubleshooting

Here are some issues we've encountered when installing Upeat on different devices. We hope [this page](build/CommonIssues.md) can help you resolve them.
