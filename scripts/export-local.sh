set -euo pipefail

. scripts/params.sh

docker exec \
  dallinger \
  psynet export --local \
  | sed \
  -e "s:/tmp/dallinger_develop/:${PWD}/:" \
  -e "s:\"/PsyNet/":"\"${PSYNET_LOCAL_PATH}/:" \
  -e "s: /psynet-exports: ${PSYNET_EXPORT_STORAGE}:"
