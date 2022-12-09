echo "Note: SSH support in requirements.txt is not yet supported for Windows and Linux hosts (to be fixed soon)"

. scripts/params.sh

DOCKER_BUILDKIT=1
docker build . -t "${EXPERIMENT_IMAGE}"

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
  -e SKIP_DEPENDENCY_CHECK=1
  -e DALLINGER_NO_EGG_BUILD=1 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v  ~/.ssh:/root/.ssh \
  -v "${PWD}":/experiment \
  "${EXPERIMENT_IMAGE}" \
  dallinger docker-ssh deploy \
  --app-name "${APPNAME}"



# TODO - incorporate the following OS-specific instructions from Silvio
#    # On Linux you can use:
#    alias docker-dallinger='docker run --rm -ti -v /etc/group:/etc/group -v ~/.docker:/root/.docker -v ~/.local/share/dallinger/:/root/.local/share/dallinger/ -e HOME=/root -e DALLINGER_NO_EGG_BUILD=1 -v /var/run/docker.sock:/var/run/docker.sock -v $(readlink -f $SSH_AUTH_SOCK):/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent -v ${PWD}:/experiment  ${EXPERIMENT_IMAGE} dallinger'
#
#    # On Mac Os you can use:
#    alias docker-dallinger='docker run --rm -ti -v /etc/group:/etc/group -v ~/.docker:/root/.docker -v ~/.local/share/dallinger/:/root/.local/share/dallinger/ -e HOME=/root -e DALLINGER_NO_EGG_BUILD=1 -v /var/run/docker.sock:/var/run/docker.sock -v  ~/.ssh:/root/.ssh -v ${PWD}:/experiment  ${EXPERIMENT_IMAGE} dallinger'
