if test -f Dockertag; then
  export EXPERIMENT_IMAGE=$(cat Dockertag)
else
  export EXPERIMENT_IMAGE=psynet-experiment
fi

export REMOTE_DEBUGGER_PORT=12345
export DOCKER_BUILDKIT=1
export PSYNET_LOCAL_PATH="${HOME}"/PsyNet
export DALLINGER_LOCAL_PATH="${HOME}"/Dallinger
export PSYNET_DEBUG_STORAGE="${HOME}"/psynet-debug-storage
export PSYNET_EXPORT_STORAGE="${HOME}"/psynet-exports
