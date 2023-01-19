# Running instructions

There are various commands for running and interacting with PsyNet experiments.
We are still working on updating all of them to run with Docker. However, the
main principle is that you write commands of the following form:

```shell
bash docker/psynet debug local  # Debug the experiment locally
```

There are several commands like this that will soon be fully documented on PsyNet's 
[documentation website](https://psynetdev.gitlab.io/PsyNet).
Please make sure you have followed the instructions in INSTALL.md before trying them.

## Advanced usage

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

(Note for advanced users: if you make the file _executable_ you can omit the `bash` and just 
write `docker/psynet debug local`.)
