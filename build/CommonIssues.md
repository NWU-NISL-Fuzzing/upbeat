## Building Dockerfile

- When running Dockerfile, we met some network problem:

```
Err:1 http://archive.ubuntu.com/ubuntu focal InRelease
  Could not connect to archive.ubuntu.com:80 (91.189.91.82), connection timed out Could not connect to archive.ubuntu.com:80 (185.125.190.36), connection timed out Could not connect to archive.ubuntu.com:80 (91.189.91.83), connection timed out Could not connect to archive.ubuntu.com:80 (91.189.91.81), connection timed out
... ...
```

You can try to add the following content in Dockerfile.

```
ENV http_proxy="[YOUR IP]"
ENV https_proxy="[YOUR IP]"
```
