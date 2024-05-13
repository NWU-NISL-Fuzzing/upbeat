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

## Run

Step1. Generate test cases.

```
cd src/Generate
python main.py
```

There are two steps of test case generation: (1) assemble code segments and (2) generate callable inputs. Generated test cases are stored in `result_db`.

Step2. Execute test cases.

```
cd src/Fuzzing
python hybrid_testing.py
```

Each test case will first be applied on language-level testing, with execution information stored in table `originResult_cw`. In case of any anomalies, relevant information will be logged in table `differentialResult_cw`. 

If no anomalies are detected, the test case proceeds to the differential testing, where results are stored in table `originResult_sim` and `differentialResult_sim`.

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

UPBEAT are capable of filtering the anomalies into three types: (1) bugs that already analized (save in `bug.txt`), (2) faulty that already analized (save in `faulty.txt`), (3) new anomalies awaiting verification (save in `new_anomalies.txt`). 

## Reproduction

The bug data is located in [this page](data/result/BugList.mdresult). 
