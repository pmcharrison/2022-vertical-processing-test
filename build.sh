EXPERIMENT_IMAGE=consonance-dichotic-stretching

DOCKER_BUILDKIT=1
docker build . -t ${EXPERIMENT_IMAGE}
