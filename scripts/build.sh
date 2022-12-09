. scripts/params.sh

echo "Building the experiment's Docker image and tagging it $EXPERIMENT_IMAGE..."

DOCKER_BUILDKIT=1 \
  docker build \
  --build-arg PSYNET_DEVELOPER_MODE="${PSYNET_DEVELOPER_MODE-}" \
  -t "${EXPERIMENT_IMAGE}" \
  .
