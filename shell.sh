EXPERIMENT_IMAGE=psynet-experiment
DOCKER_BUILDKIT=1

docker build -t ${EXPERIMENT_IMAGE} .

docker run -it --rm psynet-experiment sh
