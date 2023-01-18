set -euo pipefail

. docker/params.sh

docker exec \
  -it \
  dallinger \
  /bin/bash
