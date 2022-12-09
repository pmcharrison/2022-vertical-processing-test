set -euo pipefail

. scripts/params.sh

docker exec \
  -it \
  dallinger \
  /bin/bash
