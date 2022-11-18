EXPERIMENT_IMAGE=consonance-dichotic-stretching

DOCKER_BUILDKIT=1
docker build . -t ${EXPERIMENT_IMAGE}

printf "\n"
echo "Please enter an app name (e.g. exp-2):"
read -r APPNAME

docker run \
  --rm \
  -ti \
  -v /etc/group:/etc/group \
  -v ~/.docker:/root/.docker \
  -v "${HOME}/Library/Application Support/dallinger/":/root/.local/share/dallinger/ \
  -e HOME=/root \
  -e DALLINGER_NO_EGG_BUILD=1 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v  ~/.ssh:/root/.ssh \
  -v ${PWD}:/experiment \
  ${EXPERIMENT_IMAGE} \
  dallinger docker-ssh deploy \
  --app-name "${APPNAME}"
