## Building Dockerfile

**[Issue]** 

When running Dockerfile, if you meet some network problems:

```
Err:1 http://archive.ubuntu.com/ubuntu focal InRelease
  Could not connect to archive.ubuntu.com:80 (91.189.91.82), connection timed out Could not connect to archive.ubuntu.com:80 (185.125.190.36), connection timed out Could not connect to archive.ubuntu.com:80 (91.189.91.83), connection timed out Could not connect to archive.ubuntu.com:80 (91.189.91.81), connection timed out
... ...
```

**[Solution]** 

You can try to add the following content in the Dockerfile.

```
ENV http_proxy="XXX"
ENV https_proxy="XXX"
```

## Basic Usage

**[Issue]** 

When generating test cases, no error is thrown,  but the expected output `Finished. Totally get xx test cases.` is not displayed. 

**[Solution]** 

Verify if Z3 is installed by running `pip show z3-solver`.

**[Issue]** 

It will take 20~40s when you first running `dotnet`.

**[Solution]**

Run `dotnet --version` to activate dotnet before using Upbeat.

**[Issue]**

All coverage results display as '0.0'.

**[Solution]**

There are two formats of .coverage files, which will be used in different environment. If you encounter this issue, consider utilizing an alternative parsing method available in [this file](src/Fuzzing/get_code_coverage.py). 

Specifically, you need to select an alternative regex pattern for variable declaration between lines 27 and 28, and ensure that all matching statements correspond with either the first or the second regex pattern.