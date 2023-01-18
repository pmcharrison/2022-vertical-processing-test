#!/bin/bash

set -euo pipefail

. docker/params.sh

./docker/run.sh psynet "$@" \
  | sed -e "s:/tmp/dallinger_develop/:${PWD}/:" -e "s:\"/PsyNet/":"\"${PSYNET_LOCAL_PATH}/:"
