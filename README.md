# UPBEAT (Updating)

UPBEAT is a fuzzing tool to generate random test cases for bugs related to input checking in Q# libraries.

## Getting Started

1. Check that your setup meets the REQUIREMENTS.md.
2. Follow the installation instructions in INSTALL.md.

## Run

Step1. Generate test cases.

UPBEAT will generate test cases 

```
cd src/Generate
python main.py
```

You can find a sample in `src/Fuzzing/qsharpPattern/Program.qs`.

Step2. Execute test cases.

Each test case will first be applied on language-level testing, with execution information stored in table `originResult_cw`. In case of any anomalies, relevant information will be logged in table `differentialResult_cw`. If no anomalies are detected, the test case proceeds to the differential testing, where results are stored in table `originResult_sim` and `differentialResult_sim`.

```
cd src/Fuzzing
python hybrid_testing.py
```

Step3. Filter anomalies.

UPBEAT are capable of filtering the anomalies into three types: (1) bugs that already analized (save in `bug.txt`), (2) faulty that already analized (save in `faulty.txt`), (3) new anomalies awaiting verification (save in `new_anomalies.txt`). 

```
cd src/Fuzzing
python history_bug_filter.py
```
