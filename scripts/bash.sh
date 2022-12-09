set -euo pipefail

. scripts/params.sh
. scripts/services.sh
. scripts/build.sh


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
