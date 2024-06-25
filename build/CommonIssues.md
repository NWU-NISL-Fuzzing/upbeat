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
