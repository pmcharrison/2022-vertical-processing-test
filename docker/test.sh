set -euo pipefail

. docker/params.sh
. docker/services.sh
. docker/build.sh

# Note: any changes to this command should be propagated to terminal.sh
docker run \
  --name dallinger \
  --rm \
  -ti \
  -u $(id -u "${USER}"):$(id -g "${USER}") \
  -v "${PWD}":/experiment \
  -v "${HOME}"/.dallingerconfig:/.dallingerconfig \
  -v "$PSYNET_DEBUG_STORAGE"/tests:/psynet-debug-storage \
  -v "$PSYNET_EXPORT_STORAGE"/tests:/psynet-data/export \
  --network dallinger \
  -e FLASK_OPTIONS='-h 0.0.0.0' \
  -e REDIS_URL=redis://dallinger_redis:6379 \
  -e DATABASE_URL=postgresql://dallinger:dallinger@dallinger_postgres/dallinger \
  -e PSYNET_DEVELOPER_MODE="${PSYNET_DEVELOPER_MODE:-}" \
  -v "${PSYNET_LOCAL_PATH}":/PsyNet \
  "${EXPERIMENT_IMAGE}" \
  pytest test.py \
  | sed -e "s:/tmp/dallinger_develop/:${PWD}/:" -e "s:\"/PsyNet/":"\"${PSYNET_LOCAL_PATH}/:"

#-p 5000:5000 \