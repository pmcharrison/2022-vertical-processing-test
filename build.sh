echo "Building the experiment's Docker image and tagging it $EXPERIMENT_IMAGE..."

DOCKER_BUILDKIT=1 \
  docker build \
  --build-arg PSYNET_EDITABLE="${PSYNET_EDITABLE-}" \
  -t "${EXPERIMENT_IMAGE}" \
  .
