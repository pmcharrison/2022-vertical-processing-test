#!/bin/bash

set -euo pipefail

. docker/params

./docker/run psynet "$@" \
  | sed -e "s:/tmp/dallinger_develop/:${PWD}/:" -e "s:\"/PsyNet/":"\"${PSYNET_LOCAL_PATH}/:"
