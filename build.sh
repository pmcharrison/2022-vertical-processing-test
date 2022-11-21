echo "Building the experiment's Docker image and tagging it $EXPERIMENT_IMAGE..."
docker build . -t "${EXPERIMENT_IMAGE}"
