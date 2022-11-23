# syntax = docker/dockerfile:1.2
#
# Note - the syntax of this Dockerfile differs in several ways from the sample Dockerfile
# provided in the Dallinger documentation.
#
# - We do not use constraints.txt because generating this file requires a local pip-compile installation
#   which goes against the no-installation philosophy. Instead of constraints.txt providing the defininitive
#   account of the installed packages, this responsibility now falls to the built Docker image.
# - We install the full requirements.txt rather than filtering out packages that are already present in the base image.
#   This simplifies the logic and ensures that experimenters can specify package versions precisely if they want.
#   The small performance overhead is mostly eliminated by caching.

FROM registry.gitlab.com/computational-audition-lab/psynet:v10-draft

RUN mkdir /experiment
WORKDIR /experiment

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

WORKDIR /

ARG PSYNET_EDITABLE
RUN if [[ "$PSYNET_EDITABLE" = 1 ]] ; then pip install -e /PsyNet ; fi

WORKDIR /experiment

COPY . /experiment

ENV PORT=5000

## We can remove this once the latest PsyNet image builds
#ENV PSYNET_IN_DOCKER=1
#RUN mkdir /psynet-debug-storage
#RUN mkdir /psynet-exports
##

CMD dallinger_heroku_web
