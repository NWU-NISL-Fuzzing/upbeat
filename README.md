# UPBEAT (Updating)

UPBEAT is a fuzzing tool to generate random test cases for bugs related to input checking in Q# libraries.

## Getting Started

1. Check that your setup meets the REQUIREMENTS.md.
2. Follow the installation instructions in INSTALL.md.
3. Adjust [the configuration file](src/config.json) to align with your specific requirements. Below are the configurable parameters and their descriptions:

```
work_dir:       The directory path where the repository is located.
testcaseCount:  The number of test cases to be generated and executed.
level:          Time to combine code fragments. Default is set to 1.
ingredient_table_name : Table name of code fragments,
reference_db:   Path to the API constraint database.
corpus_db:      Path to the code fragment database.
history_db:     Path to the historical bug database.
result_db:      Path of the result database.
projectPattern: Path to the Q# projects used during the testing phase.
boundaryValue:  Special values for random input generation.
```

## Basic Usage

Step1. Generate test cases.

```
cd src/Generate
python main.py
```

There are two steps in test case generation: (1) assemble code segments and (2) generate callable inputs. All generated test cases are stored in `result_db`.

Step2. Execute test cases.

```
cd src/Fuzzing
python hybrid_testing.py
```

Each test case will first be applied on language-level testing, with execution information stored in table `originResult_cw`. If any anomalies occurred, relevant information will be logged in table `differentialResult_cw`. 

If no anomalies are detected, the test case proceeds to differential testing, where results are stored in table `originResult_sim` and `differentialResult_sim`.

Users can also execute these two steps separately by running the following command:

```
python boundary_value_testing.py
python differential_testing.py
```

Step3. Filter anomalies.

```
cd src/Fuzzing
python history_bug_filter.py
```

UPBEAT is capable of filtering the anomalies into three types: (1) bugs that have already been analyzed (save in `bug.txt`), (2) faulty that have already been analyzed (save in `faulty.txt`), (3) new anomalies awaiting verification (save in `new_anomalies.txt`). 

## Jupyter Notebook

We provide two notebooks, a [demo notebook](jupyter/demo.ipynb) for a quick insight of all steps in Upbeat, and a [reproduction notebook](jupyter/reproduction.ipynb) to reproduce our experiment. Users can use our notebooks in two ways: launching it on your local machine or exploring it [online]().

To run the notebook on your computer, follow these simple steps:

```
cd jupyter
jupyter notebook
```

This will open the notebook in your default web browser, allowing you to interact with it seamlessly.

## Experimental Result

+ (RQ1) The bug data can be found in [this page](data/result/BugList.md). 
+ (RQ2) The coverage data is organized into two folders, [one](data/experiment/cov-result-origin) stores the original coverage values of four libraries, and [another](data/experiment/cov-result-calculated) stores the calculated weighted averages of coverage.
+ (RQ2) The anomalous behaviors found by baseline methods and Upbeat. Anomalous detected via language-level testing are stored in [this folder](data/experiment/anomalies-lang), and ones via differential testing are stored in [this folder](data/experiment/anomalies-diff).
+ (RQ3) The results of ablation study can be found in [this folder](data/experiment/ablation-study)
+ (RQ4) The evaluation of constraint extraction can be found in [this folder](data/experiment/constraint-extraction)
