set -euo pipefail

. params.sh
. services.sh
. build.sh

# Note: any changes to this command should be propagated to terminal.sh
docker run \
  --name dallinger-terminal \
  --rm \
  -ti \
  -u $(id -u "${USER}"):$(id -g "${USER}") \
  -v "${PWD}":/experiment \
  -v "${HOME}"/.dallingerconfig:/.dallingerconfig \
  -v "${HOME}"/psynet-debug-storage:/psynet-debug-storage \
  --network dallinger \
  -e REDIS_URL=redis://dallinger_redis:6379 \
  -e DATABASE_URL=postgresql://dallinger:dallinger@dallinger_postgres/dallinger \
  "${EXPERIMENT_IMAGE}" \
  /bin/bash

#  -p 5000:5000 \
#  -e FLASK_OPTIONS='-h 0.0.0.0' \