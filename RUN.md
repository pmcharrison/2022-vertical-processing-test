# Running instructions

There are various commands for running and interacting with PsyNet experiments.
We are still working on updating all of them to run with Docker. However, the
main principle is that you write commands of the following form:

```shell
bash docker/psynet debug local  # Debug the experiment locally

bash docker/psynet export local  # Export data from a local experiment
```

There are several commands like this that will soon be fully documented on PsyNet's 
[documentation website](https://psynetdev.gitlab.io/PsyNet).
Please make sure you have followed the instructions in INSTALL.md before trying them.

## Advanced usage

### Running with local installations of PsyNet and Dallinger

This experiment makes heavy use of the Python packages PsyNet and Dallinger.
If you want to debug either of these packages, it is useful to run your 
experiment with local installations of them. The first step is to 
download the source code for these packages and store in them in your 
home directory under their default names as downloaded from source control
(i.e. `~/PsyNet` and `~/Dallinger` respectively). Then you can run your 
experiment as before, but writing `psynet-dev` instead of `psynet, 
for example:

```shell
# Debug the experiment locally with developer installations of 
# PsyNet and Dallinger.
bash docker/psynet-dev debug local 
```

You can change Python code in these packages, save it, then refresh
the browser, and the app should restart with the new code
(note: this hot-refreshing does not yet apply to non-Python assets
such as JavaScript or HTML).

### Running without bash

It is possible to shorten the above command on MacOS and Linux if you first
make the shell scripts in the `docker` folder executable. 
You can do this by running the following command in your working directory:

```shell
chmod +x docker/*
```

You can then invoke the commands like this:

```shell
docker/psynet debug local
```

### Running without Docker

If you are planning to run PsyNet in a local Python installation (i.e. without Docker)
then you can use the same commands but just omitting `bash docker/`, so for example:

```shell
psynet debug local
```
