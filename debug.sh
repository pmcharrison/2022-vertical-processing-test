EXPERIMENT_IMAGE=consonance-dichotic-stretching
DOCKER_BUILDKIT=1

docker build . -t ${EXPERIMENT_IMAGE}

docker run \
  --name dallinger \
  --rm \
  -ti \
  -u $(id -u "${USER}"):$(id -g "${USER}") \
  -v "${PWD}":/experiment \
  -v "${HOME}"/.dallingerconfig:/.dallingerconfig \
  --network dallinger \
  -p 5000:5000 \
  -e FLASK_OPTIONS='-h 0.0.0.0' \
  -e REDIS_URL=redis://dallinger_redis:6379 \
  -e DATABASE_URL=postgresql://dallinger:dallinger@dallinger_postgres/dallinger \
  ${EXPERIMENT_IMAGE} \
  psynet debug \
  | sed "s:/tmp/dallinger_develop:${PWD}:"
