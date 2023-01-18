#!/bin/bash

set -euo pipefail

. docker/params.sh
. docker/services.sh
. docker/build.sh

docker rm dallinger &> /dev/null || true

docker run \
  --name dallinger \
  --rm \
  -ti \
  -u $(id -u "${USER}"):$(id -g "${USER}") \
  -v /etc/group:/etc/group \
  -v ~/.docker:/root/.docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${SSH_VOLUME}" \
  -v "${HOME}/Library/Application Support/dallinger/":/.local/share/dallinger/ \
  -v "${PWD}":/experiment \
  -v "${HOME}"/.dallingerconfig:/.dallingerconfig \
  -v "$PSYNET_DEBUG_STORAGE":/psynet-debug-storage \
  -v "$PSYNET_EXPORT_STORAGE":/psynet-data/export \
  --network dallinger \
  -p 5000:5000 \
  -e SKIP_DEPENDENCY_CHECK=1 \
  -e DALLINGER_NO_EGG_BUILD=1 \
  -e FLASK_OPTIONS='-h 0.0.0.0' \
  -e REDIS_URL=redis://dallinger_redis:6379 \
  -e DATABASE_URL=postgresql://dallinger:dallinger@dallinger_postgres/dallinger \
  -e PSYNET_DEVELOPER_MODE="${PSYNET_DEVELOPER_MODE:-}" \
  -v "${PSYNET_LOCAL_PATH}":/PsyNet \
  -v "${DALLINGER_LOCAL_PATH}":/dallinger \
  "${EXPERIMENT_IMAGE}" \
  "$@"

#  /bin/bash -c "psynet --version"

#  "$@"
