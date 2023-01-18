if test -f Dockertag; then
  export EXPERIMENT_IMAGE=$(cat Dockertag)
else
  export EXPERIMENT_IMAGE=psynet-experiment
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  export PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  export PLATFORM="macos"
elif [[ "$OSTYPE" == "cygwin" ]]; then
  export PLATFORM="windows"
elif [[ "$OSTYPE" == "msys" ]]; then
  export PLATFORM="windows"
else
  echo "Unsupported operating system: ${OSTYPE}"
  exit 1
fi

export REMOTE_DEBUGGER_PORT=12345
export DOCKER_BUILDKIT=1
export PSYNET_LOCAL_PATH="${HOME}"/PsyNet
export DALLINGER_LOCAL_PATH="${HOME}"/Dallinger
export PSYNET_DEBUG_STORAGE="${HOME}"/psynet-debug-storage
export PSYNET_EXPORT_STORAGE="${HOME}"/psynet-data/export

if [[ "$PLATFORM" == "linux" ]]; then
  SSH_VOLUME="$(readlink -f "$SSH_AUTH_SOCK"):/ssh-agent"
elif [[ "$PLATFORM" == "macos" ]]; then
  SSH_VOLUME=~/.ssh:/root/.ssh
elif [[ "$PLATFORM" == "windows" ]]; then
  SSH_VOLUME="$(readlink -f "$SSH_AUTH_SOCK"):/ssh-agent"
else
  echo "Unsupported operating system: ${PLATFORM}"
  exit 1
fi